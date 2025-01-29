"""Tests for base facts liability calculations."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from ...models import Liability, Plan
from ...calculations.base_facts.liabilities import (
    LiabilityFact,
    calculate_liability_value,
    aggregate_liabilities_by_category,
    calculate_total_liabilities
)
from ...calculations.base_facts import OwnerType

# Test Data
SAMPLE_LIABILITIES = [
    {
        'value': 500000.0,
        'owner': 'Joint',
        'include_in_nest_egg': 1,
        'liability_category_id': 1,
        'liability_name': 'Mortgage',
        'interest_rate': 0.045
    },
    {
        'value': 25000.0,
        'owner': 'Person 1',
        'include_in_nest_egg': 1,
        'liability_category_id': 2,
        'liability_name': 'Car Loan',
        'interest_rate': 0.065
    },
    {
        'value': 15000.0,
        'owner': 'Person 2',
        'include_in_nest_egg': 0,
        'liability_category_id': 2,
        'liability_name': 'Personal Loan',
        'interest_rate': None
    }
]

@pytest.fixture
def sample_liability():
    """Create a sample liability for testing."""
    return LiabilityFact.from_db_row(SAMPLE_LIABILITIES[0])  # Using Mortgage as default test liability

@pytest.fixture
def real_liabilities(db_session):
    """Load real liabilities from Test Household A (plan_id=1)."""
    stmt = select(Liability).join(Plan).filter(Plan.plan_id == 1)
    liabilities = db_session.execute(stmt).scalars().all()
    return [LiabilityFact.from_db_row({
        'value': liability.value,
        'owner': liability.owner,
        'include_in_nest_egg': liability.include_in_nest_egg,
        'liability_category_id': liability.liability_category_id,
        'liability_name': liability.liability_name,
        'interest_rate': liability.interest_rate
    }) for liability in liabilities]

def calculate_expected_compound_interest(principal: float, rate: float, years: float) -> float:
    """Helper function to calculate expected compound interest values using Decimal."""
    p = Decimal(str(principal))
    r = Decimal(str(rate))
    y = Decimal(str(years))
    result = p * (Decimal('1') + r) ** y
    return float(result.quantize(Decimal('0.01')))

def test_liability_fact_creation():
    """Test creation of LiabilityFact from database row."""
    liability = LiabilityFact.from_db_row(SAMPLE_LIABILITIES[0])
    assert liability.value == 500000.0
    assert liability.owner == OwnerType.JOINT
    assert liability.include_in_nest_egg == True
    assert liability.category_id == 1
    assert liability.name == 'Mortgage'
    assert liability.interest_rate == 0.045

def test_liability_fact_creation_no_interest():
    """Test creation of LiabilityFact without interest rate."""
    liability = LiabilityFact.from_db_row(SAMPLE_LIABILITIES[2])
    assert liability.value == 15000.0
    assert liability.interest_rate is None

def test_calculate_liability_value_no_interest(sample_liability):
    """Test liability value calculation with no interest rate."""
    liability = LiabilityFact.from_db_row(SAMPLE_LIABILITIES[2])  # Personal Loan
    result = calculate_liability_value(liability, date.today())
    assert result['current_value'] == 15000.0
    assert result['projected_value'] is None
    assert result['interest_rate'] is None
    assert result['included_in_totals'] == False

def test_calculate_liability_value_with_interest(sample_liability):
    """Test liability value calculation with interest rate."""
    base_date = date(2025, 1, 1)
    calculation_date = base_date + timedelta(days=365)
    
    result = calculate_liability_value(sample_liability, calculation_date, base_date)
    expected = calculate_expected_compound_interest(500000.0, 0.045, 1.0)
    
    assert result['current_value'] == 500000.0
    assert result['projected_value'] is not None
    assert abs(result['projected_value'] - expected) < 0.01
    assert result['interest_rate'] == 0.045
    assert result['included_in_totals'] == True

def test_calculate_liability_value_partial_year():
    """Test liability value calculation for partial year."""
    liability = LiabilityFact.from_db_row(SAMPLE_LIABILITIES[1])  # Car Loan
    base_date = date(2025, 1, 1)
    calculation_date = base_date + timedelta(days=182)
    
    result = calculate_liability_value(liability, calculation_date, base_date)
    expected = calculate_expected_compound_interest(25000.0, 0.065, 182/365)
    
    assert result['current_value'] == 25000.0
    assert abs(result['projected_value'] - expected) < 0.01

def test_aggregate_liabilities_by_category():
    """Test grouping and calculating liabilities by category."""
    liabilities = [LiabilityFact.from_db_row(row) for row in SAMPLE_LIABILITIES]
    base_date = date(2025, 1, 1)
    results = aggregate_liabilities_by_category(liabilities, base_date)
    
    assert len(results) == 2  # Two categories
    assert 1 in results  # Mortgage category
    assert 2 in results  # Loans category
    assert len(results[2]) == 2  # Two loans in category 2
    
    # Check category 2 current total
    category_2_total = sum(r['current_value'] for r in results[2])
    assert abs(category_2_total - 40000.0) < 0.01  # 25000 + 15000

def test_calculate_total_liabilities():
    """Test calculation of total liability value."""
    liabilities = [LiabilityFact.from_db_row(row) for row in SAMPLE_LIABILITIES]
    base_date = date(2025, 1, 1)
    result = calculate_total_liabilities(liabilities, base_date)
    
    # Only included liabilities: Mortgage (500000) + Car Loan (25000)
    assert abs(result['current_value'] - 525000.0) < 0.01
    assert result['metadata']['liability_count'] == 3
    assert result['metadata']['included_count'] == 2

def test_calculate_total_liabilities_with_projection():
    """Test calculation of total liability value with future projection."""
    liabilities = [LiabilityFact.from_db_row(row) for row in SAMPLE_LIABILITIES]
    base_date = date(2025, 1, 1)
    calculation_date = base_date + timedelta(days=365)
    
    result = calculate_total_liabilities(liabilities, calculation_date, base_date)
    
    # Calculate expected values for included liabilities
    mortgage_projected = calculate_expected_compound_interest(500000.0, 0.045, 1.0)
    car_loan_projected = calculate_expected_compound_interest(25000.0, 0.065, 1.0)
    expected_total = mortgage_projected + car_loan_projected
    
    assert abs(result['projected_value'] - expected_total) < 0.01

def test_real_data_liability_calculations(real_liabilities):
    """Test calculations with real data from the database."""
    calculation_date = date(2025, 1, 1)
    result = calculate_total_liabilities(real_liabilities, calculation_date)
    
    # Sum the values directly, convert to Decimal at the end
    expected_total = sum(
        liability.value for liability in real_liabilities 
        if liability.include_in_nest_egg
    )
    expected_total = Decimal(str(expected_total)).quantize(Decimal('0.01'))
    
    assert abs(result['current_value'] - float(expected_total)) < 0.01

def test_real_data_category_aggregation(real_liabilities):
    """Test category aggregation with real data."""
    calculation_date = date(2025, 1, 1)
    results = aggregate_liabilities_by_category(real_liabilities, calculation_date)
    
    categories = {liability.category_id for liability in real_liabilities}
    assert set(results.keys()) == categories
    
    for category_id in categories:
        category_liabilities = [l for l in real_liabilities if l.category_id == category_id]
        category_total = float(sum(
            Decimal(str(r['current_value'])) for r in results[category_id]
        ).quantize(Decimal('0.01')))
        expected_total = float(sum(
            Decimal(str(l.value)) for l in category_liabilities
        ).quantize(Decimal('0.01')))
        
        assert abs(category_total - expected_total) < 0.01
