from typing import Union, List
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, Context

# Precision settings
CALCULATION_PRECISION = 8
DISPLAY_PRECISION = 2
CALCULATION_CONTEXT = Context(prec=CALCULATION_PRECISION, rounding=ROUND_HALF_UP)

def to_decimal(amount: Union[float, str, Decimal]) -> Decimal:
    """Converts amount to Decimal with high precision."""
    try:
        return CALCULATION_CONTEXT.create_decimal(str(amount)) if not isinstance(amount, Decimal) else CALCULATION_CONTEXT.create_decimal(amount)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid decimal conversion: {amount}") from e

def to_float(amount: Decimal) -> float:
    """Converts Decimal to float with 2 decimal place rounding."""
    return float(round_to_currency(amount))

def apply_annual_compound_rate(principal: Decimal, rate: Decimal) -> Decimal:
    """Applies annual compound rate to principal."""
    try:
        return principal * (to_decimal('1') + to_decimal(rate))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid compound calculation: principal={principal}, rate={rate}") from e

def apply_annual_inflation(amount: Decimal, inflation_rate: Decimal) -> Decimal:
    """Adjusts amount for annual inflation."""
    return apply_annual_compound_rate(amount, inflation_rate)

def combine_amounts(amounts: List[Decimal]) -> Decimal:
    """Sums multiple Decimal amounts with precision."""
    try:
        return sum((to_decimal(amt) for amt in amounts), to_decimal('0'))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amounts for combination: {amounts}") from e

def round_to_currency(amount: Decimal) -> Decimal:
    """Rounds amount to 2 decimal places."""
    try:
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid currency rounding: {amount}") from e
