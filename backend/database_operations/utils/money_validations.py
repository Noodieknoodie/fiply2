def validate_positive_amount(amount: float, field_name: str) -> None:
    """Validate financial amounts are positive values. Required for: assets, liabilities, scheduled inflows, scheduled outflows, retirement income, and retirement spending."""

def validate_rate(rate: float, field_name: str) -> None:
    """Validate growth rate, inflation rate, or interest rate is numeric and within valid bounds. Can be negative as per core validation rules."""

def validate_stepwise_growth_config(periods: List[Tuple[int, float]], field_name: str) -> None:
    """Validate stepwise growth periods are in chronological order and don't overlap. Required for asset-specific growth rate configurations."""