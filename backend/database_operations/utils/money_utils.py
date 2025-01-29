"""Money handling utilities for financial calculations.

This module provides standardized monetary calculations with precise decimal handling.
All calculations use Python's Decimal type to avoid floating point errors.
Growth and inflation are applied at the start of each year.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

def to_decimal(amount: Union[float, str, Decimal]) -> Decimal:
    """Convert a float/str to Decimal, ensuring string conversion for precision.
    
    Handles floating point precision issues by rounding to 8 decimal places
    before converting to Decimal. This ensures that values like 0.1 + 0.2
    are properly converted to 0.3 instead of 0.30000000000000004.
    """
    if isinstance(amount, Decimal):
        return amount
    if isinstance(amount, float):
        # Round float to 8 decimal places to handle precision issues
        return Decimal(format(amount, '.8f')).normalize()
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

def apply_annual_growth(amount: Decimal, rate: Decimal) -> Decimal:
    """Apply annual growth rate to an amount.
    
    Growth is applied as a simple multiplication: amount * (1 + rate)
    
    Args:
        amount: Base amount to grow
        rate: Annual growth rate as decimal (0.05 = 5%)
        
    Returns:
        Amount after growth, rounded to 2 decimal places
        
    Example:
        >>> apply_annual_growth(Decimal('1000.00'), Decimal('0.05'))
        Decimal('1050.00')
    """
    growth_factor = Decimal('1') + rate
    return (amount * growth_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def apply_annual_inflation(amount: Decimal, rate: Decimal) -> Decimal:
    """Apply annual inflation rate to an amount.
    
    Inflation is applied at the start of each year before other calculations.
    Uses same formula as growth: amount * (1 + rate)
    
    Args:
        amount: Base amount to adjust
        rate: Annual inflation rate as decimal (0.03 = 3%)
        
    Returns:
        Inflation-adjusted amount, rounded to 2 decimal places
        
    Example:
        >>> apply_annual_inflation(Decimal('1000.00'), Decimal('0.03'))
        Decimal('1030.00')
    """
    return apply_annual_growth(amount, rate)  # Same calculation as growth 