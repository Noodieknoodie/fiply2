# backend/database_operations/tests/database_tests/test_base_facts_retirement_income.py

"""Tests for base facts retirement income calculations."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from ...calculations.base_facts.retirement_income import (
    RetirementIncomeFact,
    calculate_retirement_income_value,
    aggregate_retirement_income_by_owner,
    calculate_total_retirement_income
)
from ...calculations.base_facts import OwnerType

# Test Data
BASE_DATE = date(2025, 1, 1)
PERSON1_DOB = date(1960, 1, 1)  # 65 in 2025
PERSON2_DOB = date(1962, 1, 1)  # 63 in 2025
ONE_YEAR_LATER = BASE_DATE + timedelta(days=365)
TWO_YEARS_LATER = BASE_DATE + timedelta(days=365 * 2)

SAMPLE_RETIREMENT_INCOMES = [
    {  # Social Security - starts immediately in 2025
        'annual_income': 50000.0,
        'name': 'Social Security',
        'owner': 'Person 1',
        'start_age': 65,
        'end_age': None,
        'include_in_nest_egg': True,
        'apply_inflation': True
    },
    {  # Pension - starts in 2027 (age 67)
        'annual_income': 24000.0,
        'name': 'Pension',
        'owner': 'Person 1',
        'start_age': 67,
        'end_age': 85,
        'include_in_nest_egg': True,
        'apply_inflation': False
    },
    {  # Spouse's Social Security - starts in 2027 (age 65)
        'annual_income': 30000.0,
        'name': 'Spouse Social Security',
        'owner': 'Person 2',
        'start_age': 65,
        'end_age': None,
        'include_in_nest_egg': True,
        'apply_inflation': True
    }
]

@pytest.fixture
def sample_income():
    """Create a sample retirement income for testing."""
    return RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[0])

def test_retirement_income_fact_creation():
    """Test creation of RetirementIncomeFact from database row."""
    income = RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[0])
    assert income.annual_income == 50000.0
    assert income.name == 'Social Security'
    assert income.owner == OwnerType.PERSON_1
    assert income.start_age == 65
    assert income.end_age is None
    assert income.include_in_nest_egg == True
    assert income.apply_inflation == True

def test_calculate_retirement_income_value_not_yet_active():
    """Test retirement income calculation before start age."""
    income = RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[1])  # Pension starts at 67
    result = calculate_retirement_income_value(income, BASE_DATE, PERSON1_DOB)
    
    assert result['annual_amount'] == 24000.0
    assert result['adjusted_amount'] == 0.0
    assert result['is_active'] == False
    assert result['inflation_applied'] == False

def test_calculate_retirement_income_value_with_inflation():
    """Test retirement income calculation with inflation adjustment."""
    income = RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[0])  # Social Security
    result = calculate_retirement_income_value(
        income,
        ONE_YEAR_LATER,
        PERSON1_DOB,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    expected = float(
        (Decimal('50000') * (Decimal('1') + Decimal('0.03')))
        .quantize(Decimal('0.01'))
    )
    
    assert result['annual_amount'] == 50000.0
    assert abs(result['adjusted_amount'] - expected) < 0.01
    assert result['is_active'] == True
    assert result['inflation_applied'] == True

def test_calculate_retirement_income_value_no_inflation():
    """Test retirement income calculation without inflation adjustment."""
    income = RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[1])  # Pension
    result = calculate_retirement_income_value(
        income,
        TWO_YEARS_LATER,  # Now active (age 67)
        PERSON1_DOB,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    assert result['annual_amount'] == 24000.0
    assert result['adjusted_amount'] == 24000.0
    assert result['is_active'] == True
    assert result['inflation_applied'] == False

def test_calculate_retirement_income_value_with_end_age():
    """Test retirement income calculation with end age consideration."""
    income = RetirementIncomeFact.from_db_row(SAMPLE_RETIREMENT_INCOMES[1])  # Pension ends at 85
    
    # Test at age 67 (active)
    result = calculate_retirement_income_value(
        income,
        TWO_YEARS_LATER,
        PERSON1_DOB,
        base_date=BASE_DATE
    )
    assert result['is_active'] == True
    assert result['adjusted_amount'] == 24000.0
    
    # Test at age 86 (inactive)
    future_date = date(2046, 1, 1)  # Age 86
    result = calculate_retirement_income_value(
        income,
        future_date,
        PERSON1_DOB,
        base_date=BASE_DATE
    )
    assert result['is_active'] == False
    assert result['adjusted_amount'] == 0.0

def test_aggregate_retirement_income_by_owner():
    """Test grouping and calculating retirement incomes by owner."""
    incomes = [RetirementIncomeFact.from_db_row(row) for row in SAMPLE_RETIREMENT_INCOMES]
    results = aggregate_retirement_income_by_owner(
        incomes,
        TWO_YEARS_LATER,  # 2027 - both people eligible for Social Security
        PERSON1_DOB,
        PERSON2_DOB,
        base_date=BASE_DATE
    )
    
    assert OwnerType.PERSON_1.value in results
    assert OwnerType.PERSON_2.value in results
    assert len(results[OwnerType.PERSON_1.value]) == 2  # Social Security and Pension
    assert len(results[OwnerType.PERSON_2.value]) == 1  # Spouse's Social Security
    
    # Check person1's incomes
    person1_active = [i for i in results[OwnerType.PERSON_1.value] if i['is_active']]
    assert len(person1_active) == 2
    
    # Check person2's incomes
    person2_active = [i for i in results[OwnerType.PERSON_2.value] if i['is_active']]
    assert len(person2_active) == 1

def test_calculate_total_retirement_income():
    """Test calculation of total retirement income values."""
    incomes = [RetirementIncomeFact.from_db_row(row) for row in SAMPLE_RETIREMENT_INCOMES]
    result = calculate_total_retirement_income(
        incomes,
        TWO_YEARS_LATER,  # 2027 - all incomes active
        PERSON1_DOB,
        PERSON2_DOB,
        base_date=BASE_DATE
    )
    
    # At 2027: All incomes active (50000 + 24000 + 30000)
    expected_total = 104000.0
    assert abs(result['total_income'] - expected_total) < 0.01
    
    assert result['metadata']['incomes']['total'] == 3
    assert result['metadata']['incomes']['active'] == 3

def test_calculate_total_retirement_income_with_inflation():
    """Test calculation of total retirement income with inflation adjustment."""
    incomes = [RetirementIncomeFact.from_db_row(row) for row in SAMPLE_RETIREMENT_INCOMES]
    result = calculate_total_retirement_income(
        incomes,
        TWO_YEARS_LATER,
        PERSON1_DOB,
        PERSON2_DOB,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    # Calculate expected values with inflation
    ss_with_inflation = float(
        (Decimal('50000') * (Decimal('1') + Decimal('0.03')) ** Decimal('2'))
        .quantize(Decimal('0.01'))
    )
    spouse_ss_with_inflation = float(
        (Decimal('30000') * (Decimal('1') + Decimal('0.03')) ** Decimal('2'))
        .quantize(Decimal('0.01'))
    )
    pension_no_inflation = 24000.0
    
    expected_total = ss_with_inflation + spouse_ss_with_inflation + pension_no_inflation
    assert abs(result['total_income'] - expected_total) < 0.01 