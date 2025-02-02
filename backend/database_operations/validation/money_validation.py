from typing import Dict, Union
from decimal import Decimal

def validate_positive_amount(amount: Union[float, Decimal], field_name: str) -> None:
    """
    Validate financial amounts are positive values. Required for: assets, liabilities, 
    scheduled inflows, scheduled outflows, retirement income, and retirement spending.
    """
    if not isinstance(amount, (float, Decimal)):
        raise ValueError(f"{field_name} must be a numeric value")
    if amount <= 0:
        raise ValueError(f"{field_name} must be a positive value")

def validate_rate(rate: Union[float, Decimal], field_name: str) -> None:
    """
    Validate growth rate, inflation rate, or interest rate is numeric and within valid bounds. 
    Can be negative as per core validation rules.
    """
    if not isinstance(rate, (float, Decimal)):
        raise ValueError(f"{field_name} must be a numeric value")

def validate_owner(owner: str, field_name: str) -> None:
    """Validate owner field contains valid value ('person1', 'person2', or 'joint')."""
    valid_owners = {'person1', 'person2', 'joint'}
    if owner not in valid_owners:
        raise ValueError(f"{field_name} must be one of: {', '.join(valid_owners)}")
