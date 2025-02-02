# tests/test_money_validation.py
from database_operations.validation.money_validation import validate_positive_amount
import pytest

def test_validate_positive_amount():
    """Test amount validation"""
    with pytest.raises(ValueError):

        validate_positive_amount(-1000, "test_amount")
    with pytest.raises(ValueError):
        validate_positive_amount(0, "test_amount")
    # Should pass
    validate_positive_amount(1000, "test_amount")