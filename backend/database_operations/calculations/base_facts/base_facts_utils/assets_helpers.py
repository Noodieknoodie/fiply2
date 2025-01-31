def _get_stepwise_rate(self, config: GrowthConfig, year: int, default_rate: Decimal) -> Decimal:
    """Determines applicable rate from stepwise configuration."""

def _apply_compound_growth(self, value: Decimal, rate: Decimal, years: int) -> Decimal:
    """Applies compound growth for specified number of years."""

def _validate_growth_config(self, config: GrowthConfig) -> None:
    """Validates growth configuration structure and rates."""

def _calculate_category_totals(self, results: List[AssetCalculationResult]) -> Dict[str, Decimal]:
    """Computes running totals by category."""
