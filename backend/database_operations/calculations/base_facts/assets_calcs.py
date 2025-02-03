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

from ...models import GrowthRateConfiguration
from ...utils.money_utils import to_decimal, apply_annual_compound_rate, combine_amounts, round_to_currency
from ...validation.money_validation import validate_positive_amount, validate_rate
from ...validation.growth_validation import validate_growth_config_type, validate_stepwise_periods


@dataclass
class AssetFact:
    """Stores asset details and growth configurations."""
    asset_id: int
    value: Decimal
    category_id: int
    include_in_nest_egg: bool
    growth_configs: List[GrowthRateConfiguration]
    owner: str
    name: str


@dataclass
class AssetCalculationResult:
    """Stores results of asset growth calculations."""
    asset_id: int
    starting_value: Decimal
    ending_value: Decimal
    applied_growth_rate: Decimal
    category_id: int
    growth_amount: Decimal
    included_in_nest_egg: bool
    metadata: Dict


class AssetCalculator:
    """Handles asset valuation with growth rate application."""

    def calculate_asset_value(self, asset: AssetFact, year: int, default_rate: Decimal,
                              plan_creation_year: int) -> AssetCalculationResult:
        """Calculates asset value applying growth rates."""
        if year < plan_creation_year:
            raise ValueError(f"Cannot calculate asset value before plan creation year {plan_creation_year}")

        starting_value = asset.value
        growth_rate = self._get_applicable_growth_rate(asset.growth_configs, year, default_rate)
        ending_value = apply_annual_compound_rate(starting_value, growth_rate)
        growth_amount = ending_value - starting_value

        return AssetCalculationResult(
            asset_id=asset.asset_id,
            starting_value=starting_value,
            ending_value=ending_value,
            applied_growth_rate=growth_rate,
            category_id=asset.category_id,
            growth_amount=growth_amount,
            included_in_nest_egg=asset.include_in_nest_egg,
            metadata=self._generate_metadata(asset, year, growth_rate, growth_amount)
        )

    def calculate_multiple_assets(self, assets: List[AssetFact], year: int, default_rate: Decimal,
                                  plan_creation_year: int) -> List[AssetCalculationResult]:
        """Calculates values for multiple assets."""
        self.validate_asset_facts(assets)
        return [self.calculate_asset_value(asset, year, default_rate, plan_creation_year) for asset in assets]

    def aggregate_by_category(self, results: List[AssetCalculationResult]) -> Dict[int, Decimal]:
        """Aggregates assets by category."""
        totals: Dict[int, Decimal] = {}
        for result in results:
            totals[result.category_id] = combine_amounts([totals.get(result.category_id, Decimal('0')), result.ending_value])
        return totals

    def calculate_nest_egg_value(self, results: List[AssetCalculationResult]) -> Decimal:
        """Computes total value of nest-egg eligible assets."""
        return combine_amounts([r.ending_value for r in results if r.included_in_nest_egg])

    def _get_applicable_growth_rate(self, growth_configs: List[GrowthRateConfiguration], year: int,
                                    default_rate: Decimal) -> Decimal:
        """Determines applicable growth rate based on hierarchy."""
        for config in sorted(growth_configs, key=lambda c: c.configuration_type == 'OVERRIDE', reverse=True):
            if config.configuration_type == 'STEPWISE' and config.start_year <= year <= (config.end_year or year):
                return to_decimal(config.growth_rate)
            if config.configuration_type == 'OVERRIDE':
                return to_decimal(config.growth_rate)
        return default_rate

    def validate_asset_facts(self, assets: List[AssetFact]) -> None:
        """Validates asset values and growth configurations."""
        for asset in assets:
            validate_positive_amount(asset.value, f"asset_{asset.asset_id}_value")
            for config in asset.growth_configs:
                validate_growth_config_type(config.configuration_type, f"asset_{asset.asset_id}_growth_type")

            stepwise_periods = [{"start_year": c.start_year, "end_year": c.end_year}
                                for c in asset.growth_configs if c.configuration_type == 'STEPWISE']
            if stepwise_periods:
                validate_stepwise_periods(stepwise_periods, f"asset_{asset.asset_id}_growth_periods")

    def _generate_metadata(self, asset: AssetFact, year: int, applied_rate: Decimal, growth_amount: Decimal) -> Dict:
        """Generates metadata about asset valuation."""
        return {
            "asset_name": asset.name,
            "owner": asset.owner,
            "year": year,
            "applied_growth_rate": str(round_to_currency(applied_rate)),
            "growth_amount": str(round_to_currency(growth_amount)),
            "rate_type": self._determine_rate_type(asset.growth_configs, year)
        }

    def _determine_rate_type(self, growth_configs: List[GrowthRateConfiguration], year: int) -> str:
        """Determines the type of applied growth rate."""
        for config in growth_configs:
            if config.configuration_type == 'STEPWISE' and config.start_year <= year <= (config.end_year or year):
                return 'STEPWISE'
            if config.configuration_type == 'OVERRIDE':
                return 'OVERRIDE'
        return 'DEFAULT'
