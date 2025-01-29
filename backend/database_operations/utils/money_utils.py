"""Money handling utilities for financial calculations."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

def to_decimal(amount: Union[float, str, Decimal]) -> Decimal:
    """Convert a float/str to Decimal, ensuring string conversion for precision."""
    if isinstance(amount, Decimal):
        return amount
    return Decimal(str(amount))

def to_float(amount: Decimal) -> float:
    """Convert a Decimal to float with 2 decimal places."""
    return float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def validate_money(amount: float, field_name: str) -> None:
    """Validate a monetary amount is positive and has max 2 decimal places."""
    if amount < 0:
        raise ValueError(f"{field_name} must be positive")
    decimal_str = str(amount)
    if '.' in decimal_str:
        decimals = len(decimal_str.split('.')[1])
        if decimals > 2:
            raise ValueError(f"{field_name} must have at most 2 decimal places")

def validate_rate(rate: float, field_name: str) -> None:
    """Validate a rate is between 0 and 1."""
    if not 0 <= rate <= 1:
        raise ValueError(f"{field_name} must be between 0 and 1") 