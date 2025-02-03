# backend/database_operations/validation/money_validation.py
from typing import Union
from decimal import Decimal

def validate_positive_amount(amount: Union[float, Decimal], field_name: str) -> None:
    """Raises ValueError if amount is not a positive number."""
    if not isinstance(amount, (float, Decimal)):
        raise ValueError(f"{field_name} must be numeric")
    if amount <= 0:
        raise ValueError(f"{field_name} must be positive")

def validate_rate(rate: Union[float, Decimal], field_name: str) -> None:
    """Raises ValueError if rate is not numeric."""
    if not isinstance(rate, (float, Decimal)):
        raise ValueError(f"{field_name} must be numeric")

def validate_owner(owner: str, field_name: str) -> None:
    """Raises ValueError if owner is not 'person1', 'person2', or 'joint'."""
    if owner not in {"person1", "person2", "joint"}:
        raise ValueError(f"{field_name} must be 'person1', 'person2', or 'joint'")
