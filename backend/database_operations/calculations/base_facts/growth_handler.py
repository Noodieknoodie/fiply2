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
from datetime import date

from ...models import GrowthRateConfiguration
from ...utils.money_utils import to_decimal, apply_annual_compound_rate
from ...utils.validation_utils import validate_rate

@dataclass
class GrowthResult:
    """Container for growth calculation results and metadata."""
    final_value: Decimal
    growth_amount: Decimal
    applied_rate: Decimal
    rate_source: str  # 'default', 'override', or 'stepwise'
    period_start: Optional[int] = None  # For stepwise only
    period_end: Optional[int] = None    # For stepwise only

class GrowthRateHandler:
    """Central authority for all asset growth rate calculations."""
    
    def apply_growth(
        self,
        value: Decimal,
        asset_id: int,
        year: int,
        default_rate: Decimal,
        growth_configs: List[GrowthRateConfiguration]
    ) -> GrowthResult:
        """
        Apply growth to a value following the strict growth rate hierarchy.
        """
        rate, source, period = self._get_applicable_rate(growth_configs, year, default_rate)
        final_value = apply_annual_compound_rate(value, rate)
        growth_amount = final_value - value
        
        return GrowthResult(
            final_value=final_value,
            growth_amount=growth_amount,
            applied_rate=rate,
            rate_source=source,
            period_start=period[0] if period else None,
            period_end=period[1] if period else None
        )

    def _get_applicable_rate(
        self,
        configs: List[GrowthRateConfiguration],
        year: int,
        default_rate: Decimal
    ) -> Tuple[Decimal, str, Optional[Tuple[int, int]]]:
        """Determines applicable growth rate following strict hierarchy."""
        stepwise_configs = [c for c in configs if c.configuration_type == 'STEPWISE']
        
        for config in stepwise_configs:
            if config.start_year <= year and (config.end_year is None or config.end_year >= year):
                return to_decimal(config.growth_rate), 'stepwise', (config.start_year, config.end_year)
        
        override_configs = [c for c in configs if c.configuration_type == 'OVERRIDE']
        if override_configs:
            return to_decimal(override_configs[0].growth_rate), 'override', None
        
        return default_rate, 'default', None

    def validate_stepwise_configurations(self, configs: List[GrowthRateConfiguration]) -> None:
        """Validates stepwise growth configurations don't overlap."""
        sorted_configs = sorted([c for c in configs if c.configuration_type == 'STEPWISE'], key=lambda x: x.start_year)
        for i in range(len(sorted_configs) - 1):
            if sorted_configs[i].end_year and sorted_configs[i].end_year >= sorted_configs[i + 1].start_year:
                raise ValueError(f"Overlapping growth periods: {sorted_configs[i].start_year}-{sorted_configs[i].end_year} and {sorted_configs[i + 1].start_year}-{sorted_configs[i + 1].end_year}")
            validate_rate(sorted_configs[i].growth_rate)
