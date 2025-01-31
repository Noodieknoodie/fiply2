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
from ...utils.money_utils import to_decimal, apply_annual_compound_rate


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
        default_rate: Decimal
    ) -> AssetCalculationResult:
        """
        Calculates asset value for a specific year applying appropriate growth.
        
        Args:
            asset: Asset data container
            year: Year to calculate for
            default_rate: Default growth rate from base assumptions
            
        Returns:
            Calculation results including starting/ending values and metadata
        """
        starting_value = asset.value
        
        # Determine applicable growth rate
        growth_rate = self._get_applicable_growth_rate(
            asset.growth_configs,
            year,
            default_rate
        )
        
        # Apply growth
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
        default_rate: Decimal
    ) -> List[AssetCalculationResult]:
        """
        Calculates values for multiple assets.
        
        Args:
            assets: List of assets to calculate
            year: Year to calculate for
            default_rate: Default growth rate
            
        Returns:
            List of calculation results for each asset
        """
        return [
            self.calculate_asset_value(asset, year, default_rate)
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
        totals = {}
        for result in results:
            cat_id = result.category_id
            if cat_id not in totals:
                totals[cat_id] = Decimal('0')
            totals[cat_id] += result.ending_value
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
        return sum(
            r.ending_value 
            for r in results 
            if r.included_in_nest_egg
        )

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
                return to_decimal(config.growth_rate)
        
        # Check for simple override
        if override_configs:
            return to_decimal(override_configs[0].growth_rate)
        
        # Fall back to default
        return default_rate

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
            'applied_growth_rate': str(applied_rate),
            'growth_amount': str(growth_amount),
            'rate_type': self._determine_rate_type(asset.growth_configs, year)
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

    def validate_asset_facts(self, assets: List[AssetFact]) -> None:
        """Validates asset inputs before calculations."""
        for asset in assets:
            if asset.value < 0:
                raise ValueError(
                    f"Asset {asset.asset_id} has negative value"
                )
            
            # Validate growth configurations
            stepwise_periods = [
                (c.start_year, c.end_year)
                for c in asset.growth_configs
                if c.configuration_type == 'STEPWISE'
            ]
            
            # Check for overlapping periods
            for i, (start1, end1) in enumerate(stepwise_periods):
                for start2, end2 in stepwise_periods[i+1:]:
                    if end1 is None or end2 is None:
                        continue
                    if not (end1 < start2 or end2 < start1):
                        raise ValueError(
                            f"Asset {asset.asset_id} has overlapping growth periods"
                        )

