from typing import Union, List
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, Context

# Constants for precision handling
CALCULATION_PRECISION = 8  # High precision for internal calculations
DISPLAY_PRECISION = 2     # Standard currency display precision
CALCULATION_CONTEXT = Context(prec=CALCULATION_PRECISION, rounding=ROUND_HALF_UP)

def to_decimal(amount: Union[float, str, Decimal]) -> Decimal:
    """Convert float/string to Decimal with standardized precision handling. Handles floating point precision issues by rounding to 8 decimal places."""
    try:
        if isinstance(amount, Decimal):
            return CALCULATION_CONTEXT.create_decimal(amount)
        return CALCULATION_CONTEXT.create_decimal(str(amount))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amount for decimal conversion: {amount}") from e

def to_float(amount: Decimal) -> float:
    """Convert Decimal to float with standardized 2 decimal place rounding for calculation results."""
    try:
        # Use display precision for float conversion to avoid floating point artifacts
        rounded = round_to_currency(amount)
        return float(rounded)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid decimal for float conversion: {amount}") from e

def apply_annual_compound_rate(principal: Decimal, rate: Decimal) -> Decimal:
    """Apply annual compound rate following the core principle that all events occur at year boundaries. Growth compounds annually."""
    try:
        # Convert rate to decimal format (e.g., 0.05 for 5%)
        rate_decimal = to_decimal(rate)
        # Formula: principal * (1 + rate)
        multiplier = to_decimal('1') + rate_decimal
        result = principal * multiplier
        return CALCULATION_CONTEXT.create_decimal(result)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid values for compound calculation: principal={principal}, rate={rate}") from e

def apply_annual_inflation(amount: Decimal, inflation_rate: Decimal) -> Decimal:
    """Apply annual inflation adjustment. Inflation adjustments compound annually and are applied at the start of each year."""
    try:
        # Inflation is essentially the same calculation as compound rate
        return apply_annual_compound_rate(amount, inflation_rate)
    except ValueError as e:
        raise ValueError(f"Invalid values for inflation calculation: amount={amount}, rate={inflation_rate}") from e

def combine_amounts(amounts: List[Decimal]) -> Decimal:
    """Combine multiple decimal amounts while maintaining precision. Used for aggregating portfolio values and ensuring consistent handling of precision across calculations."""
    try:
        # Convert all amounts to high precision decimals before summing
        converted_amounts = [to_decimal(amt) for amt in amounts]
        total = sum(converted_amounts, start=to_decimal('0'))
        return CALCULATION_CONTEXT.create_decimal(total)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amounts in list for combination: {amounts}") from e

def round_to_currency(amount: Decimal) -> Decimal:
    """Round decimal to standard currency precision (2 decimal places) with proper handling of edge cases. Used for final display values and ensures consistent rounding across the application."""
    try:
        # Create a new context for display precision
        display_context = Context(prec=DISPLAY_PRECISION, rounding=ROUND_HALF_UP)
        # Quantize ensures exact decimal places
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amount for currency rounding: {amount}") from e