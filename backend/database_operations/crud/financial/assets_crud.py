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

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import Asset, AssetCategory, GrowthRateConfiguration, Plan
from ...validation.money_validation import (
    validate_positive_amount,
    validate_rate,
    validate_owner
)
from ...utils.money_utils import to_decimal, to_float
from ...validation.growth_validation import validate_stepwise_periods

class AssetCRUD:
    """CRUD operations for asset and growth rate management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_asset(
        self,
        plan_id: int,
        asset_category_id: int,
        asset_name: str,
        value: Union[float, str, Decimal],
        owner: str,
        include_in_nest_egg: bool = True,
        growth_config: Optional[Dict[str, Any]] = None
    ) -> Asset:
        """
        Create a new asset with optional growth rate configuration.
        
        Args:
            plan_id: ID of plan this asset belongs to
            asset_category_id: ID of asset category
            asset_name: Name identifier for the asset
            value: Current value of the asset
            owner: Owner of the asset ('person1', 'person2', or 'joint')
            include_in_nest_egg: Whether to include in retirement calculations
            growth_config: Optional growth rate configuration
            
        Returns:
            Newly created Asset instance
            
        Raises:
            ValueError: If validation fails
            NoResultFound: If plan_id or category_id don't exist
            IntegrityError: If database constraint violated
        """
        # Verify plan and category exist
        stmt = select(Plan).join(AssetCategory).where(
            and_(
                Plan.plan_id == plan_id,
                AssetCategory.asset_category_id == asset_category_id
            )
        )
        if not self.session.execute(stmt).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} or category {asset_category_id} not found")

        # Convert to Decimal for validation
        decimal_value = to_decimal(value)
        
        # Validate input
        validate_positive_amount(decimal_value, "asset_value")
        validate_owner(owner, "owner")

        # Convert to float for DB storage
        db_value = to_float(decimal_value)

        # Create asset instance
        asset = Asset(
            plan_id=plan_id,
            asset_category_id=asset_category_id,
            asset_name=asset_name,
            value=db_value,
            owner=owner,
            include_in_nest_egg=include_in_nest_egg
        )
        
        try:
            self.session.add(asset)
            self.session.flush()  # Get asset_id without committing

            # Add growth configuration if provided
            if growth_config:
                self._add_growth_configuration(asset.asset_id, growth_config)

            self.session.commit()
            return asset

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create asset", orig=e)

    def get_asset(
        self, 
        asset_id: int,
        include_growth_config: bool = False
    ) -> Optional[Asset]:
        """
        Retrieve an asset by ID.
        
        Args:
            asset_id: Primary key of asset
            include_growth_config: If True, eagerly loads growth configuration
            
        Returns:
            Asset instance if found, None otherwise
        """
        stmt = select(Asset).where(Asset.asset_id == asset_id)
        
        if include_growth_config:
            stmt = stmt.options(joinedload(Asset.growth_rates))
            
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_assets(
        self, 
        plan_id: int,
        category_id: Optional[int] = None
    ) -> List[Asset]:
        """
        Retrieve all assets for a plan, optionally filtered by category.
        
        Args:
            plan_id: ID of plan to get assets for
            category_id: Optional category ID to filter by
            
        Returns:
            List of Asset instances
        """
        stmt = select(Asset).where(Asset.plan_id == plan_id)
        
        if category_id:
            stmt = stmt.where(Asset.asset_category_id == category_id)
            
        return list(self.session.execute(stmt).scalars().all())

    def update_asset(
        self,
        asset_id: int,
        update_data: Dict[str, Any],
        growth_config: Optional[Dict[str, Any]] = None
    ) -> Optional[Asset]:
        """
        Update an asset and optionally its growth configuration.
        
        Args:
            asset_id: Primary key of asset to update
            update_data: Dictionary of fields to update and their new values
            growth_config: Optional new growth rate configuration
            
        Returns:
            Updated Asset instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Handle value conversion and validation if present
        if 'value' in update_data:
            decimal_value = to_decimal(update_data['value'])
            validate_positive_amount(decimal_value, "asset_value")
            update_data['value'] = to_float(decimal_value)

        # Validate owner if included in update
        if 'owner' in update_data:
            validate_owner(update_data['owner'], "owner")

        try:
            # Update asset
            stmt = (
                update(Asset)
                .where(Asset.asset_id == asset_id)
                .values(**update_data)
                .returning(Asset)
            )
            result = self.session.execute(stmt)
            asset = result.scalar_one_or_none()
            
            if not asset:
                return None

            # Update growth configuration if provided
            if growth_config:
                # Remove existing configuration
                stmt = delete(GrowthRateConfiguration).where(
                    GrowthRateConfiguration.asset_id == asset_id
                )
                self.session.execute(stmt)
                
                # Add new configuration
                self._add_growth_configuration(asset_id, growth_config)

            self.session.commit()
            return asset

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update asset", orig=e)

    def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset.
        
        Args:
            asset_id: Primary key of asset to delete
            
        Returns:
            True if asset was deleted, False if not found
        """
        stmt = delete(Asset).where(Asset.asset_id == asset_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def _add_growth_configuration(
        self,
        asset_id: int,
        config: Dict[str, Any]
    ) -> None:
        """
        Add growth rate configuration for an asset.
        
        Args:
            asset_id: ID of asset to configure
            config: Growth configuration dictionary
            
        Raises:
            ValueError: If validation fails
        """
        # Get the asset's plan to check creation year
        stmt = select(Plan).join(Asset).where(Asset.asset_id == asset_id)
        plan = self.session.execute(stmt).scalar_one()
        
        if not plan.plan_creation_year:
            raise ValueError("Plan creation year must be set before configuring growth rates")
            
        config_type = config.get('configuration_type')
        if config_type not in ['DEFAULT', 'OVERRIDE', 'STEPWISE']:
            raise ValueError("Invalid growth configuration type")

        if config_type == 'STEPWISE':
            # Validate stepwise configuration
            periods = config.get('periods', [])
            
            # Validate periods don't start before plan creation
            for period in periods:
                if period['start_year'] < plan.plan_creation_year:
                    raise ValueError(f"Growth period cannot start before plan creation year {plan.plan_creation_year}")
            
            validate_stepwise_periods(periods, "growth_periods")
            
            # Create configuration for each period
            for period in periods:
                rate_decimal = to_decimal(period['growth_rate'])
                validate_rate(rate_decimal, "growth_rate")
                growth_config = GrowthRateConfiguration(
                    asset_id=asset_id,
                    configuration_type='STEPWISE',
                    start_year=period['start_year'],
                    end_year=period['end_year'],
                    growth_rate=to_float(rate_decimal)
                )
                self.session.add(growth_config)
        else:
            # Simple override configuration
            rate_decimal = to_decimal(config.get('growth_rate'))
            validate_rate(rate_decimal, "growth_rate")
            growth_config = GrowthRateConfiguration(
                asset_id=asset_id,
                configuration_type=config_type,
                start_year=plan.plan_creation_year,  # Default to plan creation year for non-stepwise
                end_year=config.get('end_year'),
                growth_rate=to_float(rate_decimal)
            )
            self.session.add(growth_config)

    def get_asset_summary(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of asset information including growth configuration.
        
        Args:
            asset_id: Primary key of asset
            
        Returns:
            Dictionary containing asset summary if found, None otherwise
        """
        asset = self.get_asset(asset_id, include_growth_config=True)
        if not asset:
            return None
            
        growth_config = None
        if asset.growth_rates:
            if len(asset.growth_rates) == 1:
                config = asset.growth_rates[0]
                growth_config = {
                    'type': config.configuration_type,
                    'rate': config.growth_rate
                }
            else:
                growth_config = {
                    'type': 'STEPWISE',
                    'periods': [
                        {
                            'start_year': config.start_year,
                            'end_year': config.end_year,
                            'rate': config.growth_rate
                        }
                        for config in sorted(
                            asset.growth_rates,
                            key=lambda x: x.start_year
                        )
                    ]
                }
            
        return {
            'asset_id': asset.asset_id,
            'asset_name': asset.asset_name,
            'category_id': asset.asset_category_id,
            'value': asset.value,
            'owner': asset.owner,
            'include_in_nest_egg': asset.include_in_nest_egg,
            'growth_configuration': growth_config
        }