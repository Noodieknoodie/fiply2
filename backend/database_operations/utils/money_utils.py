def to_decimal(amount: Union[float, str, Decimal]) -> Decimal:
    """Convert float/string to Decimal with standardized precision handling. Handles floating point precision issues by rounding to 8 decimal places."""

def to_float(amount: Decimal) -> float:
    """Convert Decimal to float with standardized 2 decimal place rounding for calculation results."""

def apply_annual_compound_rate(principal: Decimal, rate: Decimal) -> Decimal:
    """Apply annual compound rate following the core principle that all events occur at year boundaries. Growth compounds annually."""

def apply_annual_inflation(amount: Decimal, inflation_rate: Decimal) -> Decimal:
    """Apply annual inflation adjustment. Inflation adjustments compound annually and are applied at the start of each year."""