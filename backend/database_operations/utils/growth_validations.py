def validate_growth_config_type(config_type: str) -> None:
    """Validate growth configuration type is one of: DEFAULT, OVERRIDE, or STEPWISE."""

def validate_growth_period_boundaries(periods: List[Dict], start_year: int, end_year: int) -> None:
    """Validate growth periods fall within overall projection timeline."""

def validate_growth_period_sequence(periods: List[Dict]) -> None:
    """Validate growth periods are sequential and non-overlapping."""
