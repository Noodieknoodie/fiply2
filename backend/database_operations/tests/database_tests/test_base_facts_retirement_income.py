# backend/database_operations/tests/database_tests/test_base_facts_retirement_income.py

"""Tests for retirement income calculations.

This test suite verifies the year-based retirement income calculations,
demonstrating how retirement income is tracked and calculated on a yearly basis.
"""

import pytest
from decimal import Decimal
from ...calculations.base_facts.retirement_income import (
    RetirementIncomeFact,
    calculate_retirement_income_value,
    aggregate_retirement_income_by_owner,
    calculate_total_retirement_income,
    OwnerType
)

# Test Data
SAMPLE_RETIREMENT_INCOMES = [
    # Social Security - starts at age 65
    RetirementIncomeFact(
        annual_income=50000.00,
        owner=OwnerType.PERSON_1,
        include_in_nest_egg=True,
        name="Social Security",
        start_age=65,
        end_age=None,
        apply_inflation=True,
        person_dob="1960-01-01"  # Age 65 in 2025
    ),
    # Pension - starts at age 67, ends at age 85
    RetirementIncomeFact(
        annual_income=24000.00,
        owner=OwnerType.PERSON_1,
        include_in_nest_egg=True,
        name="Pension",
        start_age=67,
        end_age=85,
        apply_inflation=False,
        person_dob="1960-01-01"  # Age 67 in 2027
    ),
    # Spouse's Social Security - starts at age 65
    RetirementIncomeFact(
        annual_income=30000.00,
        owner=OwnerType.PERSON_2,
        include_in_nest_egg=True,
        name="Spouse Social Security",
        start_age=65,
        end_age=None,
        apply_inflation=True,
        person_dob="1962-01-01"  # Age 65 in 2027
    )
]


def test_retirement_income_activation():
    """Test when retirement income becomes active based on age."""
    income = SAMPLE_RETIREMENT_INCOMES[0]  # Social Security at 65
    
    # Before retirement age (2024 - age 64)
    result = calculate_retirement_income_value(income, 2024)
    assert not result['is_active']
    assert result['adjusted_amount'] == 0.0
    
    # At retirement age (2025 - age 65)
    result = calculate_retirement_income_value(income, 2025)
    assert result['is_active']
    assert result['adjusted_amount'] == 50000.00
    
    # After retirement age (2026 - age 66)
    result = calculate_retirement_income_value(income, 2026)
    assert result['is_active']
    assert result['adjusted_amount'] == 50000.00


def test_retirement_income_with_end_age():
    """Test retirement income with end age consideration."""
    income = SAMPLE_RETIREMENT_INCOMES[1]  # Pension ends at 85
    
    # At start age (2027 - age 67)
    result = calculate_retirement_income_value(income, 2027)
    assert result['is_active']
    assert result['adjusted_amount'] == 24000.00
    
    # During active years (2040 - age 80)
    result = calculate_retirement_income_value(income, 2040)
    assert result['is_active']
    assert result['adjusted_amount'] == 24000.00
    
    # After end age (2046 - age 86)
    result = calculate_retirement_income_value(income, 2046)
    assert not result['is_active']
    assert result['adjusted_amount'] == 0.0


def test_inflation_adjustment():
    """Test inflation adjustments over multiple years."""
    income = SAMPLE_RETIREMENT_INCOMES[0]  # Social Security with inflation
    inflation_rate = 0.03  # 3% inflation
    
    # Start year - no inflation yet
    result = calculate_retirement_income_value(income, 2025, inflation_rate)
    assert result['adjusted_amount'] == 50000.00
    assert not result['inflation_applied']
    
    # One year of inflation
    result = calculate_retirement_income_value(income, 2026, inflation_rate, base_year=2025)
    assert result['adjusted_amount'] == 51500.00
    assert result['inflation_applied']
    
    # Two years of inflation
    result = calculate_retirement_income_value(income, 2027, inflation_rate, base_year=2025)
    assert abs(result['adjusted_amount'] - 53045.00) < 0.01


def test_owner_aggregation():
    """Test aggregation of retirement income by owner."""
    year = 2027  # Both people have active income
    inflation_rate = 0.03
    
    aggregated = aggregate_retirement_income_by_owner(SAMPLE_RETIREMENT_INCOMES, year, inflation_rate, base_year=2025)
    
    # Should have both owners
    assert OwnerType.PERSON_1.value in aggregated
    assert OwnerType.PERSON_2.value in aggregated
    
    # Person 1 should have both Social Security and Pension active
    person1_incomes = aggregated[OwnerType.PERSON_1.value]
    assert len(person1_incomes) == 2
    assert all(income['is_active'] for income in person1_incomes)
    
    # Person 2 should have Social Security active
    person2_incomes = aggregated[OwnerType.PERSON_2.value]
    assert len(person2_incomes) == 1
    assert all(income['is_active'] for income in person2_incomes)


def test_total_calculations():
    """Test calculation of total retirement income values."""
    year = 2027  # All incomes active
    inflation_rate = 0.03
    
    totals = calculate_total_retirement_income(SAMPLE_RETIREMENT_INCOMES, year, inflation_rate, base_year=2025)
    
    # Expected values for 2027:
    # - Person 1 Social Security: 53,045.00 (with 2 years inflation)
    # - Person 1 Pension: 24,000.00 (no inflation)
    # - Person 2 Social Security: 30,000.00 (just started, no inflation yet)
    # Total: 107,045.00
    assert abs(totals['total_income'] - 107045.00) < 0.01
    assert abs(totals['nest_egg_income'] - 107045.00) < 0.01  # All included in nest egg
    
    assert totals['metadata']['incomes']['total'] == 3
    assert totals['metadata']['incomes']['active'] == 3


def test_base_year_override():
    """Test using a different base year for inflation calculations."""
    income = SAMPLE_RETIREMENT_INCOMES[0]  # Social Security with inflation
    inflation_rate = 0.03
    
    # Calculate with default base year (2025 - start year)
    result1 = calculate_retirement_income_value(income, 2027, inflation_rate)
    
    # Calculate with explicit earlier base year
    result2 = calculate_retirement_income_value(income, 2027, inflation_rate, base_year=2024)
    
    # Should have more inflation applied with earlier base year
    assert result2['adjusted_amount'] > result1['adjusted_amount']


def test_decimal_precision():
    """Test handling of decimal precision in calculations."""
    # Create an income with an odd amount to test rounding
    income = RetirementIncomeFact(
        annual_income=50000.33,
        owner=OwnerType.PERSON_1,
        include_in_nest_egg=True,
        name="Test",
        start_age=65,
        end_age=None,
        apply_inflation=True,
        person_dob="1960-01-01"
    )
    
    result = calculate_retirement_income_value(income, 2025)
    
    # Should maintain 2 decimal places
    assert isinstance(result['annual_amount'], float)
    assert str(result['annual_amount']).split('.')[1] == '33' 