"""Tests for money handling utilities.

This test suite verifies precise decimal handling and growth calculations.
All monetary values use Decimal for accuracy.
"""

import pytest
from decimal import Decimal
from ...utils.money_utils import (
    to_decimal,
    to_float,
    validate_money,
    validate_rate,
    apply_annual_growth,
    apply_annual_inflation
)


def test_to_decimal():
    """Test conversion to Decimal type."""
    test_cases = [
        (1000.00, Decimal('1000.00')),
        ('1000.00', Decimal('1000.00')),
        (Decimal('1000.00'), Decimal('1000.00')),
        (0.1 + 0.2, Decimal('0.3')),  # Handles float precision issues
    ]
    
    for input_val, expected in test_cases:
        assert to_decimal(input_val) == expected


def test_to_float():
    """Test conversion from Decimal to float."""
    test_cases = [
        (Decimal('1000.00'), 1000.00),
        (Decimal('0.30'), 0.30),
        (Decimal('100.555'), 100.56),  # Tests rounding
    ]
    
    for input_val, expected in test_cases:
        assert to_float(input_val) == expected


def test_validate_money():
    """Test monetary value validation."""
    # Valid cases
    validate_money(1000.00, "test_amount")
    validate_money(0.50, "test_amount")
    
    # Invalid cases
    with pytest.raises(ValueError):
        validate_money(-1.00, "test_amount")
    
    with pytest.raises(ValueError):
        validate_money(1.234, "test_amount")


def test_validate_rate():
    """Test rate validation."""
    # Valid cases
    validate_rate(0.0, "test_rate")
    validate_rate(0.05, "test_rate")
    validate_rate(1.0, "test_rate")
    
    # Invalid cases
    with pytest.raises(ValueError):
        validate_rate(-0.01, "test_rate")
    
    with pytest.raises(ValueError):
        validate_rate(1.01, "test_rate")


def test_apply_annual_growth():
    """Test annual growth calculations."""
    test_cases = [
        # (initial, rate, expected)
        (Decimal('1000.00'), Decimal('0.05'), Decimal('1050.00')),  # 5% growth
        (Decimal('1000.00'), Decimal('0.00'), Decimal('1000.00')),  # No growth
        (Decimal('0.00'), Decimal('0.05'), Decimal('0.00')),        # Zero amount
        (Decimal('1000.00'), Decimal('1.00'), Decimal('2000.00')),  # 100% growth
    ]
    
    for initial, rate, expected in test_cases:
        result = apply_annual_growth(initial, rate)
        assert result == expected
        assert isinstance(result, Decimal)


def test_apply_annual_inflation():
    """Test annual inflation adjustments."""
    test_cases = [
        # (initial, rate, expected)
        (Decimal('1000.00'), Decimal('0.03'), Decimal('1030.00')),  # 3% inflation
        (Decimal('1000.00'), Decimal('0.00'), Decimal('1000.00')),  # No inflation
        (Decimal('0.00'), Decimal('0.03'), Decimal('0.00')),        # Zero amount
    ]
    
    for initial, rate, expected in test_cases:
        result = apply_annual_inflation(initial, rate)
        assert result == expected
        assert isinstance(result, Decimal)


def test_decimal_precision():
    """Test decimal precision handling."""
    amount = Decimal('1000.00')
    rate = Decimal('0.033333')  # Many decimal places
    
    result = apply_annual_growth(amount, rate)
    
    # Should round to 2 decimal places
    assert str(result).split('.')[1] == '33'  # 1033.33
    assert isinstance(result, Decimal) 