# backend/database_operations/crud/financial/growth_rates.py

"""
Full CRUD operations for growth configurations following SQLAlchemy 2.0 style
Support for all three configuration types:
Default (base rate)
Override (fixed rate)
Stepwise (multiple periods)
Proper validation of:
Configuration types
Growth rates
Year sequences
Target specification
Support for multiple targets:
Assets
Retirement income
Scenarios
Special handling for stepwise configurations
Comprehensive configuration summary
Utility for determining applicable rate
Proper error handling and transaction management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...models import GrowthRateConfiguration, Asset, RetirementIncomePlan, Scenario
from ...validation.money_validation import validate_rate
from ...validation.growth_validation import validate_stepwise_periods, validate_growth_config_type
from ...validation.time_validation import validate_year_not_before_plan_creation


class GrowthRateCRUD:
    """Handles CRUD operations for growth rate configurations."""

    def __init__(self, session: Session):
        self.session = session

    def create_growth_config(self, configuration_type: str, start_year: int, growth_rate: float,
                             end_year: Optional[int] = None, asset_id: Optional[int] = None,
                             retirement_income_plan_id: Optional[int] = None,
                             scenario_id: Optional[int] = None) -> GrowthRateConfiguration:
        """Creates a growth rate configuration for an asset, retirement income, or scenario."""
        validate_growth_config_type(configuration_type, "configuration_type")

        if sum(x is not None for x in [asset_id, retirement_income_plan_id, scenario_id]) != 1:
            raise ValueError("Must specify exactly one target (asset, retirement income, or scenario)")

        validate_rate(growth_rate, "growth_rate")
        if end_year is not None and start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")

        config = GrowthRateConfiguration(
            configuration_type=configuration_type, start_year=start_year, end_year=end_year,
            growth_rate=growth_rate, asset_id=asset_id, retirement_income_plan_id=retirement_income_plan_id,
            scenario_id=scenario_id
        )

        try:
            self.session.add(config)
            self.session.commit()
            return config
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create growth configuration", orig=e)

    def create_stepwise_config(self, periods: List[Dict[str, Any]], asset_id: Optional[int] = None,
                               retirement_income_plan_id: Optional[int] = None,
                               scenario_id: Optional[int] = None) -> List[GrowthRateConfiguration]:
        """Creates multiple stepwise growth rate configurations."""
        if sum(x is not None for x in [asset_id, retirement_income_plan_id, scenario_id]) != 1:
            raise ValueError("Must specify exactly one target (asset, retirement income, or scenario)")

        if not validate_stepwise_periods([(p["start_year"], p["end_year"]) for p in periods]):
            raise ValueError("Stepwise periods must be chronological and non-overlapping")

        for period in periods:
            validate_rate(period["growth_rate"], "growth_rate")

        try:
            configs = [GrowthRateConfiguration(
                configuration_type="STEPWISE", start_year=p["start_year"], end_year=p["end_year"],
                growth_rate=p["growth_rate"], asset_id=asset_id, retirement_income_plan_id=retirement_income_plan_id,
                scenario_id=scenario_id
            ) for p in periods]

            self.session.add_all(configs)
            self.session.commit()
            return configs
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create stepwise configurations", orig=e)

    def get_growth_config(self, config_id: int) -> Optional[GrowthRateConfiguration]:
        """Retrieves a growth configuration by ID."""
        return self.session.execute(select(GrowthRateConfiguration).where(
            GrowthRateConfiguration.growth_rate_id == config_id)).scalar_one_or_none()

    def get_configurations_for_target(self, target_type: str, target_id: int) -> List[GrowthRateConfiguration]:
        """Retrieves all growth configurations for a given target."""
        target_map = {
            "asset": GrowthRateConfiguration.asset_id,
            "retirement_income": GrowthRateConfiguration.retirement_income_plan_id,
            "scenario": GrowthRateConfiguration.scenario_id
        }

        if target_type not in target_map:
            raise ValueError("Invalid target type")

        return list(self.session.execute(select(GrowthRateConfiguration)
                                         .where(target_map[target_type] == target_id)
                                         .order_by(GrowthRateConfiguration.start_year)).scalars().all())

    def update_growth_config(self, config_id: int, update_data: Dict[str, Any]) -> Optional[GrowthRateConfiguration]:
        """Updates a growth configuration."""
        if "configuration_type" in update_data and update_data["configuration_type"] not in {"DEFAULT", "OVERRIDE", "STEPWISE"}:
            raise ValueError("Invalid configuration type")

        if "growth_rate" in update_data:
            validate_rate(update_data["growth_rate"], "growth_rate")

        if "start_year" in update_data or "end_year" in update_data:
            config = self.get_growth_config(config_id)
            if not config:
                return None

            start_year = update_data.get("start_year", config.start_year)
            end_year = update_data.get("end_year", config.end_year)

            if end_year is not None and start_year > end_year:
                raise ValueError("Start year must be before or equal to end year")

        try:
            result = self.session.execute(update(GrowthRateConfiguration)
                                          .where(GrowthRateConfiguration.growth_rate_id == config_id)
                                          .values(**update_data)
                                          .returning(GrowthRateConfiguration))
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update growth configuration", orig=e)

    def delete_growth_config(self, config_id: int) -> bool:
        """Deletes a growth configuration."""
        result = self.session.execute(delete(GrowthRateConfiguration)
                                      .where(GrowthRateConfiguration.growth_rate_id == config_id))
        self.session.commit()
        return result.rowcount > 0

    def get_growth_config_summary(self, config_id: int) -> Optional[Dict[str, Any]]:
        """Returns a summary of a growth configuration."""
        config = self.get_growth_config(config_id)
        if not config:
            return None

        target_type, target_id = None, None
        if config.asset_id:
            target_type, target_id = "asset", config.asset_id
        elif config.retirement_income_plan_id:
            target_type, target_id = "retirement_income", config.retirement_income_plan_id
        elif config.scenario_id:
            target_type, target_id = "scenario", config.scenario_id

        return {
            "config_id": config.growth_rate_id,
            "type": config.configuration_type,
            "growth_rate": config.growth_rate,
            "start_year": config.start_year,
            "end_year": config.end_year,
            "target_type": target_type,
            "target_id": target_id,
            "is_stepwise": config.configuration_type == "STEPWISE"
        }

    def get_applicable_rate(self, year: int, target_type: str, target_id: int, default_rate: float) -> float:
        """Returns the applicable growth rate for a specific year."""
        for config in self.get_configurations_for_target(target_type, target_id):
            if config.start_year <= year and (config.end_year is None or config.end_year >= year):
                return config.growth_rate
        return default_rate
