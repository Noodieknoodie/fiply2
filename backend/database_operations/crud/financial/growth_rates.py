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

from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...models import (
    GrowthRateConfiguration,
    Asset,
    RetirementIncomePlan,
    Scenario
)
from ...utils.money_validations import validate_rate
from ...utils.time_validations import validate_stepwise_periods

class GrowthRateCRUD:
    """CRUD operations for growth rate configuration management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_growth_config(
        self,
        configuration_type: str,
        start_year: int,
        growth_rate: float,
        end_year: Optional[int] = None,
        asset_id: Optional[int] = None,
        retirement_income_plan_id: Optional[int] = None,
        scenario_id: Optional[int] = None
    ) -> GrowthRateConfiguration:
        """
        Create a new growth rate configuration.
        
        Args:
            configuration_type: Type of configuration ('DEFAULT', 'OVERRIDE', or 'STEPWISE')
            start_year: Year configuration begins
            growth_rate: Annual growth rate
            end_year: Optional year configuration ends
            asset_id: Optional ID of asset this applies to
            retirement_income_plan_id: Optional ID of retirement income this applies to
            scenario_id: Optional ID of scenario this applies to
            
        Returns:
            Newly created GrowthRateConfiguration instance
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate configuration type
        if configuration_type not in ['DEFAULT', 'OVERRIDE', 'STEPWISE']:
            raise ValueError("Invalid configuration type")

        # Validate that exactly one target is specified
        targets = [asset_id, retirement_income_plan_id, scenario_id]
        if len([t for t in targets if t is not None]) != 1:
            raise ValueError("Must specify exactly one target (asset, retirement income, or scenario)")

        # Validate rate
        validate_rate(growth_rate, "growth_rate")

        # Validate years if end_year provided
        if end_year is not None and start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")

        # Create configuration instance
        config = GrowthRateConfiguration(
            configuration_type=configuration_type,
            start_year=start_year,
            end_year=end_year,
            growth_rate=growth_rate,
            asset_id=asset_id,
            retirement_income_plan_id=retirement_income_plan_id,
            scenario_id=scenario_id
        )
        
        try:
            self.session.add(config)
            self.session.commit()
            return config
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create growth configuration", orig=e)

    def create_stepwise_config(
        self,
        periods: List[Dict[str, Any]],
        asset_id: Optional[int] = None,
        retirement_income_plan_id: Optional[int] = None,
        scenario_id: Optional[int] = None
    ) -> List[GrowthRateConfiguration]:
        """
        Create multiple growth rate configurations for stepwise growth.
        
        Args:
            periods: List of period configurations with start_year, end_year, and growth_rate
            asset_id: Optional ID of asset these apply to
            retirement_income_plan_id: Optional ID of retirement income these apply to
            scenario_id: Optional ID of scenario these apply to
            
        Returns:
            List of created GrowthRateConfiguration instances
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate that exactly one target is specified
        targets = [asset_id, retirement_income_plan_id, scenario_id]
        if len([t for t in targets if t is not None]) != 1:
            raise ValueError("Must specify exactly one target (asset, retirement income, or scenario)")

        # Validate periods don't overlap
        period_tuples = [(p['start_year'], p['end_year']) for p in periods]
        if not validate_stepwise_periods(period_tuples):
            raise ValueError("Stepwise periods must be chronological and non-overlapping")

        # Validate rates
        for period in periods:
            validate_rate(period['growth_rate'], "growth_rate")

        try:
            configs = []
            for period in periods:
                config = GrowthRateConfiguration(
                    configuration_type='STEPWISE',
                    start_year=period['start_year'],
                    end_year=period['end_year'],
                    growth_rate=period['growth_rate'],
                    asset_id=asset_id,
                    retirement_income_plan_id=retirement_income_plan_id,
                    scenario_id=scenario_id
                )
                self.session.add(config)
                configs.append(config)
                
            self.session.commit()
            return configs
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create stepwise configurations", orig=e)

    def get_growth_config(self, config_id: int) -> Optional[GrowthRateConfiguration]:
        """
        Retrieve a growth configuration by ID.
        
        Args:
            config_id: Primary key of growth configuration
            
        Returns:
            GrowthRateConfiguration instance if found, None otherwise
        """
        stmt = select(GrowthRateConfiguration).where(
            GrowthRateConfiguration.growth_rate_id == config_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_configurations_for_target(
        self,
        target_type: str,
        target_id: int
    ) -> List[GrowthRateConfiguration]:
        """
        Retrieve all growth configurations for a specific target.
        
        Args:
            target_type: Type of target ('asset', 'retirement_income', or 'scenario')
            target_id: ID of target entity
            
        Returns:
            List of GrowthRateConfiguration instances
            
        Raises:
            ValueError: If invalid target type specified
        """
        if target_type not in ['asset', 'retirement_income', 'scenario']:
            raise ValueError("Invalid target type")

        id_map = {
            'asset': GrowthRateConfiguration.asset_id,
            'retirement_income': GrowthRateConfiguration.retirement_income_plan_id,
            'scenario': GrowthRateConfiguration.scenario_id
        }

        stmt = (
            select(GrowthRateConfiguration)
            .where(id_map[target_type] == target_id)
            .order_by(GrowthRateConfiguration.start_year)
        )
        return list(self.session.execute(stmt).scalars().all())

    def update_growth_config(
        self,
        config_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[GrowthRateConfiguration]:
        """
        Update a growth configuration.
        
        Args:
            config_id: Primary key of configuration to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated GrowthRateConfiguration instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate type if included
        if 'configuration_type' in update_data:
            if update_data['configuration_type'] not in ['DEFAULT', 'OVERRIDE', 'STEPWISE']:
                raise ValueError("Invalid configuration type")

        # Validate rate if included
        if 'growth_rate' in update_data:
            validate_rate(update_data['growth_rate'], "growth_rate")

        # Validate years if updating
        if 'start_year' in update_data or 'end_year' in update_data:
            current_config = self.get_growth_config(config_id)
            if not current_config:
                return None
                
            start_year = update_data.get('start_year', current_config.start_year)
            end_year = update_data.get('end_year', current_config.end_year)
            
            if end_year is not None and start_year > end_year:
                raise ValueError("Start year must be before or equal to end year")

        try:
            stmt = (
                update(GrowthRateConfiguration)
                .where(GrowthRateConfiguration.growth_rate_id == config_id)
                .values(**update_data)
                .returning(GrowthRateConfiguration)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update growth configuration", orig=e)

    def delete_growth_config(self, config_id: int) -> bool:
        """
        Delete a growth configuration.
        
        Args:
            config_id: Primary key of configuration to delete
            
        Returns:
            True if configuration was deleted, False if not found
        """
        stmt = delete(GrowthRateConfiguration).where(
            GrowthRateConfiguration.growth_rate_id == config_id
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_growth_config_summary(self, config_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of growth configuration information.
        
        Args:
            config_id: Primary key of growth configuration
            
        Returns:
            Dictionary containing configuration summary if found, None otherwise
        """
        config = self.get_growth_config(config_id)
        if not config:
            return None
            
        target_type = None
        target_id = None
        if config.asset_id:
            target_type = 'asset'
            target_id = config.asset_id
        elif config.retirement_income_plan_id:
            target_type = 'retirement_income'
            target_id = config.retirement_income_plan_id
        elif config.scenario_id:
            target_type = 'scenario'
            target_id = config.scenario_id
            
        return {
            'config_id': config.growth_rate_id,
            'type': config.configuration_type,
            'growth_rate': config.growth_rate,
            'start_year': config.start_year,
            'end_year': config.end_year,
            'target_type': target_type,
            'target_id': target_id,
            'is_stepwise': config.configuration_type == 'STEPWISE'
        }

    def get_applicable_rate(
        self,
        year: int,
        target_type: str,
        target_id: int,
        default_rate: float
    ) -> float:
        """
        Get the applicable growth rate for a specific year.
        
        Args:
            year: Year to get rate for
            target_type: Type of target ('asset', 'retirement_income', or 'scenario')
            target_id: ID of target entity
            default_rate: Default rate to use if no override applies
            
        Returns:
            Applicable growth rate for the year
            
        Raises:
            ValueError: If invalid target type specified
        """
        configs = self.get_configurations_for_target(target_type, target_id)
        
        for config in configs:
            if config.start_year <= year and (config.end_year is None or config.end_year >= year):
                return config.growth_rate
                
        return default_rate