# backend/database_operations/crud/financial/assets.py
"""
Full CRUD operations for assets following SQLAlchemy 2.0 style
Support for all three types of growth rate configurations:
Default (no override)
Simple override
Stepwise configuration
Proper validation of:
Asset values (positive)
Growth rates
Stepwise period configuration
Owner values
Comprehensive asset summary including growth configuration
Support for filtering assets by category
Proper error handling and transaction management
Clean handling of growth rate configuration updates
"""

from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import Asset, AssetCategory, GrowthRateConfiguration, Plan
from ...validation.money_validation import validate_positive_amount, validate_rate, validate_owner
from ...utils.money_utils import to_decimal, to_float
from ...validation.growth_validation import validate_stepwise_periods


class AssetCRUD:
    """Handles CRUD operations for assets and growth rates."""

    def __init__(self, session: Session):
        self.session = session

    def create_asset(self, plan_id: int, asset_category_id: int, asset_name: str, value: Union[float, str, Decimal],
                     owner: str, include_in_nest_egg: bool = True, growth_config: Optional[Dict[str, Any]] = None) -> Asset:
        """Creates an asset with optional growth configuration."""
        if not self.session.execute(select(Plan).join(AssetCategory).where(
                and_(Plan.plan_id == plan_id, AssetCategory.asset_category_id == asset_category_id))).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} or category {asset_category_id} not found")

        decimal_value = to_decimal(value)
        validate_positive_amount(decimal_value, "asset_value")
        validate_owner(owner, "owner")

        asset = Asset(
            plan_id=plan_id, asset_category_id=asset_category_id, asset_name=asset_name,
            value=to_float(decimal_value), owner=owner, include_in_nest_egg=include_in_nest_egg
        )

        try:
            self.session.add(asset)
            self.session.flush()

            if growth_config:
                self._add_growth_configuration(asset.asset_id, growth_config)

            self.session.commit()
            return asset
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create asset", orig=e)

    def get_asset(self, asset_id: int, include_growth_config: bool = False) -> Optional[Asset]:
        """Retrieves an asset by ID."""
        stmt = select(Asset).where(Asset.asset_id == asset_id)
        if include_growth_config:
            stmt = stmt.options(joinedload(Asset.growth_rates))
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_assets(self, plan_id: int, category_id: Optional[int] = None) -> List[Asset]:
        """Retrieves all assets for a plan, optionally filtered by category."""
        stmt = select(Asset).where(Asset.plan_id == plan_id)
        if category_id:
            stmt = stmt.where(Asset.asset_category_id == category_id)
        return list(self.session.execute(stmt).scalars().all())

    def update_asset(self, asset_id: int, update_data: Dict[str, Any],
                     growth_config: Optional[Dict[str, Any]] = None) -> Optional[Asset]:
        """Updates an asset and its growth configuration if provided."""
        if "value" in update_data:
            decimal_value = to_decimal(update_data["value"])
            validate_positive_amount(decimal_value, "asset_value")
            update_data["value"] = to_float(decimal_value)

        if "owner" in update_data:
            validate_owner(update_data["owner"], "owner")

        try:
            result = self.session.execute(update(Asset)
                                          .where(Asset.asset_id == asset_id)
                                          .values(**update_data)
                                          .returning(Asset))
            asset = result.scalar_one_or_none()

            if asset and growth_config:
                self.session.execute(delete(GrowthRateConfiguration).where(GrowthRateConfiguration.asset_id == asset_id))
                self._add_growth_configuration(asset_id, growth_config)

            self.session.commit()
            return asset
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update asset", orig=e)

    def delete_asset(self, asset_id: int) -> bool:
        """Deletes an asset by ID."""
        result = self.session.execute(delete(Asset).where(Asset.asset_id == asset_id))
        self.session.commit()
        return result.rowcount > 0

    def _add_growth_configuration(self, asset_id: int, config: Dict[str, Any]) -> None:
        """Adds a growth rate configuration for an asset."""
        plan = self.session.execute(select(Plan).join(Asset).where(Asset.asset_id == asset_id)).scalar_one()
        if not plan.plan_creation_year:
            raise ValueError("Plan creation year must be set before configuring growth rates")

        config_type = config.get("configuration_type")
        if config_type not in {"DEFAULT", "OVERRIDE", "STEPWISE"}:
            raise ValueError("Invalid growth configuration type")

        if config_type == "STEPWISE":
            periods = config.get("periods", [])
            for period in periods:
                if period["start_year"] < plan.plan_creation_year:
                    raise ValueError(f"Growth period cannot start before plan creation year {plan.plan_creation_year}")
            validate_stepwise_periods(periods, "growth_periods")

            for period in periods:
                validate_rate(to_decimal(period["growth_rate"]), "growth_rate")
                self.session.add(GrowthRateConfiguration(
                    asset_id=asset_id, configuration_type="STEPWISE",
                    start_year=period["start_year"], end_year=period["end_year"],
                    growth_rate=to_float(to_decimal(period["growth_rate"]))
                ))
        else:
            validate_rate(to_decimal(config["growth_rate"]), "growth_rate")
            self.session.add(GrowthRateConfiguration(
                asset_id=asset_id, configuration_type=config_type,
                start_year=plan.plan_creation_year, end_year=config.get("end_year"),
                growth_rate=to_float(to_decimal(config["growth_rate"]))
            ))

    def get_asset_summary(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """Returns a summary of an asset, including growth configuration."""
        asset = self.get_asset(asset_id, include_growth_config=True)
        if not asset:
            return None

        growth_config = None
        if asset.growth_rates:
            if len(asset.growth_rates) == 1:
                config = asset.growth_rates[0]
                growth_config = {"type": config.configuration_type, "rate": config.growth_rate}
            else:
                growth_config = {
                    "type": "STEPWISE",
                    "periods": [{"start_year": config.start_year, "end_year": config.end_year, "rate": config.growth_rate}
                                for config in sorted(asset.growth_rates, key=lambda x: x.start_year)]
                }

        return {
            "asset_id": asset.asset_id,
            "asset_name": asset.asset_name,
            "category_id": asset.asset_category_id,
            "value": asset.value,
            "owner": asset.owner,
            "include_in_nest_egg": asset.include_in_nest_egg,
            "growth_configuration": growth_config
        }
