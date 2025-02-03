# backend/database_operations/calculations/base_facts/growth_handler.py
"""
Moved from the prior assets_helpers.py file to this file.
"""
"""
## Assets
- Growth handling:  
  1. Default: Uses base assumption growth rate  
  2. Override: Asset-specific fixed rate  
  3. Stepwise: Multiple rates over time periods
  4. Gaps in stepwise fall to default
- Optional inflation toggle
## Growth Rate System
- Assets can have default, fixed, or stepwise growth rates
- Stepwise: Multiple rates over time periods
- Gaps in stepwise fall to default
"""
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ...models import GrowthRateConfiguration
from ...utils.money_utils import to_decimal, apply_annual_compound_rate
from ...validation.money_validation import validate_rate


@dataclass
class GrowthResult:
    """Stores growth calculation results."""
    final_value: Decimal
    growth_amount: Decimal
    applied_rate: Decimal
    rate_source: str  # 'default', 'override', or 'stepwise'
    period_start: Optional[int] = None
    period_end: Optional[int] = None


class GrowthRateHandler:
    """Handles asset growth rate calculations."""

    def apply_growth(self, value: Decimal, year: int, default_rate: Decimal,
                     growth_configs: List[GrowthRateConfiguration]) -> GrowthResult:
        """Applies growth to a value based on the highest priority rate."""
        rate, source, period = self._get_applicable_rate(growth_configs, year, default_rate)
        final_value = apply_annual_compound_rate(value, rate)
        return GrowthResult(
            final_value=final_value,
            growth_amount=final_value - value,
            applied_rate=rate,
            rate_source=source,
            period_start=period[0] if period else None,
            period_end=period[1] if period else None
        )

    def _get_applicable_rate(self, configs: List[GrowthRateConfiguration], year: int,
                             default_rate: Decimal) -> Tuple[Decimal, str, Optional[Tuple[int, int]]]:
        """Determines the highest priority growth rate."""
        for config in sorted(configs, key=lambda c: (c.configuration_type != 'STEPWISE', c.start_year)):
            if config.start_year <= year and (config.end_year is None or config.end_year >= year):
                return to_decimal(config.growth_rate), config.configuration_type.lower(), (
                    config.start_year, config.end_year) if config.configuration_type == 'STEPWISE' else None
        return default_rate, 'default', None

    def validate_stepwise_configurations(self, configs: List[GrowthRateConfiguration]) -> None:
        """Ensures stepwise growth configurations do not overlap."""
        stepwise_configs = sorted([c for c in configs if c.configuration_type == 'STEPWISE'], key=lambda x: x.start_year)
        for i in range(len(stepwise_configs) - 1):
            if stepwise_configs[i].end_year and stepwise_configs[i].end_year >= stepwise_configs[i + 1].start_year:
                raise ValueError(f"Overlapping growth periods: {stepwise_configs[i].start_year}-{stepwise_configs[i].end_year} "
                                 f"and {stepwise_configs[i + 1].start_year}-{stepwise_configs[i + 1].end_year}")
            validate_rate(stepwise_configs[i].growth_rate)
