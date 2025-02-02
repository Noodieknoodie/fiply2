"""
## Assets
- Value  
- Optional category assignment  
- Growth handling:  
  1. Default: Uses base assumption growth rate  
  2. Override: Asset-specific fixed rate  
  3. Stepwise: Multiple rates over time periods (start year / end year)  
  4. Gaps in stepwise fall to default  
- Optional inflation toggle
## Growth Rate System
- Assets can have default, fixed, or stepwise growth rates
- Stepwise: Multiple rates over time periods
- Gaps in stepwise fall to default
This implementation:
1. Handles the three types of growth rates (default, override, stepwise)
2. Properly falls back to default rate when needed
3. Manages category aggregation
4. Tracks which assets are included in retirement portfolio
5. Provides detailed calculation metadata
6. Validates configurations and prevents overlapping periods
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date
from ...models import Asset, GrowthRateConfiguration
from ...utils.money_utils import (
    to_decimal, 
    apply_annual_compound_rate,
    combine_amounts,
    round_to_currency
)
from ...utils.time_utils import get_start_year_from_dob
from ...validation.money_validation import validate_positive_amount, validate_rate
from ...validation.growth_validation import (
    validate_growth_config_type,
    validate_stepwise_periods
)
@dataclass
class AssetFact:
    """Core asset data including value and growth configuration."""
    asset_id: int
    value: Decimal
    category_id: int
    include_in_nest_egg: bool
    growth_configs: List[GrowthRateConfiguration]
    owner: str
    name: str
@dataclass
class AssetCalculationResult:
    """Results container for asset calculations."""
    asset_id: int
    starting_value: Decimal
    ending_value: Decimal
    applied_growth_rate: Decimal
    category_id: int
    growth_amount: Decimal
    included_in_nest_egg: bool
    metadata: Dict
class AssetCalculator:
    """Handles asset value calculations with growth rate system."""
    def calculate_asset_value(
        self,
        asset: AssetFact,
        year: int,
        default_rate: Decimal,
        plan_creation_year: int
    ) -> AssetCalculationResult:
        """
        Calculates asset value for a specific year applying appropriate growth.
        All calculations occur at year boundaries following core principles.
        
        Args:
            asset: Asset data container
            year: Year to calculate for
            default_rate: Default growth rate from base assumptions
            plan_creation_year: Year when the plan was created
            
        Returns:
            Calculation results including starting/ending values and metadata
            
        Raises:
            ValueError: If year is before plan creation year
        """
        if year < plan_creation_year:
            raise ValueError(f"Cannot calculate asset value for year {year} before plan creation year {plan_creation_year}")
            
        starting_value = asset.value
        
        # Determine applicable growth rate
        growth_rate = self._get_applicable_growth_rate(
            asset.growth_configs,
            year,
            default_rate
        )
        
        # Apply growth at year boundary
        ending_value = apply_annual_compound_rate(
            starting_value,
            growth_rate
        )
        
        growth_amount = ending_value - starting_value
        
        return AssetCalculationResult(
            asset_id=asset.asset_id,
            starting_value=starting_value,
            ending_value=ending_value,
            applied_growth_rate=growth_rate,
            category_id=asset.category_id,
            growth_amount=growth_amount,
            included_in_nest_egg=asset.include_in_nest_egg,
            metadata=self._generate_calculation_metadata(
                asset,
                year,
                growth_rate,
                growth_amount
            )
        )
    def calculate_multiple_assets(
        self,
        assets: List[AssetFact],
        year: int,
        default_rate: Decimal,
        plan_creation_year: int
    ) -> List[AssetCalculationResult]:
        """
        Calculates values for multiple assets.
        
        Args:
            assets: List of assets to calculate
            year: Year to calculate for
            default_rate: Default growth rate
            plan_creation_year: Year when the plan was created
            
        Returns:
            List of calculation results for each asset
        """
        # Validate inputs before calculation
        self.validate_asset_facts(assets)
        
        return [
            self.calculate_asset_value(
                asset, 
                year, 
                default_rate,
                plan_creation_year
            )
            for asset in assets
        ]
    def aggregate_by_category(
        self,
        results: List[AssetCalculationResult]
    ) -> Dict[int, Decimal]:
        """
        Groups and totals assets by their categories.
        
        Args:
            results: List of asset calculation results
            
        Returns:
            Dictionary mapping category_id to total value
        """
        totals: Dict[int, Decimal] = {}
        
        for result in results:
            cat_id = result.category_id
            if cat_id not in totals:
                totals[cat_id] = Decimal('0')
            
            # Use combine_amounts for precision
            totals[cat_id] = combine_amounts([
                totals[cat_id],
                result.ending_value
            ])
            
        return totals
    def calculate_nest_egg_value(
        self,
        results: List[AssetCalculationResult]
    ) -> Decimal:
        """
        Calculates total for assets included in retirement portfolio.
        
        Args:
            results: List of asset calculation results
            
        Returns:
            Total value of retirement portfolio assets
        """
        retirement_values = [
            r.ending_value 
            for r in results 
            if r.included_in_nest_egg
        ]
        return combine_amounts(retirement_values)
    def _get_applicable_growth_rate(
        self,
        growth_configs: List[GrowthRateConfiguration],
        year: int,
        default_rate: Decimal
    ) -> Decimal:
        """
        Determines applicable growth rate following hierarchy:
        1. Stepwise rate for matching period
        2. Override rate
        3. Default rate
        """
        # Sort configs by type priority
        stepwise_configs = [
            c for c in growth_configs 
            if c.configuration_type == 'STEPWISE'
        ]
        override_configs = [
            c for c in growth_configs 
            if c.configuration_type == 'OVERRIDE'
        ]
        
        # Check stepwise first
        for config in stepwise_configs:
            if config.start_year <= year and (
                config.end_year is None or 
                config.end_year >= year
            ):
                rate = to_decimal(config.growth_rate)
                return rate
                
        # Check for simple override
        if override_configs:
            rate = to_decimal(override_configs[0].growth_rate)
            return rate
            
        return default_rate
    def validate_asset_facts(self, assets: List[AssetFact]) -> None:
        """
        Validates asset inputs before calculations.
        
        Args:
            assets: List of assets to validate
            
        Raises:
            ValueError: If validation fails
        """
        for asset in assets:
            # Validate value
            validate_positive_amount(asset.value, f"asset_{asset.asset_id}_value")
            
            # Validate growth configurations
            for config in asset.growth_configs:
                validate_growth_config_type(
                    config.configuration_type,
                    f"asset_{asset.asset_id}_growth_type"
                )
                
            # Validate stepwise periods if present
            stepwise_periods = [
                {
                    'start_year': c.start_year,
                    'end_year': c.end_year
                }
                for c in asset.growth_configs
                if c.configuration_type == 'STEPWISE'
            ]
            if stepwise_periods:
                validate_stepwise_periods(
                    stepwise_periods,
                    f"asset_{asset.asset_id}_growth_periods"
                )
    def _generate_calculation_metadata(
        self,
        asset: AssetFact,
        year: int,
        applied_rate: Decimal,
        growth_amount: Decimal
    ) -> Dict:
        """Creates metadata about calculation process."""
        return {
            'asset_name': asset.name,
            'owner': asset.owner,
            'year': year,
            'applied_growth_rate': str(round_to_currency(applied_rate)),
            'growth_amount': str(round_to_currency(growth_amount)),
            'rate_type': self._determine_rate_type(
                asset.growth_configs,
                year
            )
        }
    def _determine_rate_type(
        self,
        growth_configs: List[GrowthRateConfiguration],
        year: int
    ) -> str:
        """Determines which type of rate was applied."""
        for config in growth_configs:
            if config.configuration_type == 'STEPWISE':
                if config.start_year <= year and (
                    config.end_year is None or 
                    config.end_year >= year
                ):
                    return 'STEPWISE'
            elif config.configuration_type == 'OVERRIDE':
                return 'OVERRIDE'
        return 'DEFAULT'