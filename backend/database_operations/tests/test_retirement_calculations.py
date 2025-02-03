# tests/test_retirement_calculations.py
from decimal import Decimal
from datetime import date
import pytest
from database_operations.calculations.base_facts.retirement_income_calcs import RetirementIncomeCalculator
from database_operations.models import RetirementIncomePlan, RetirementIncomeType
from database_operations.utils.time_utils import get_age_in_year, get_year_for_age

def test_retirement_income_activation():
    """Test retirement income activation based on age."""
    calc = RetirementIncomeCalculator()
    income = RetirementIncomePlan(
        name="Social Security",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=67,
        dob=date(1970, 1, 1)
    )
    
    # Before retirement age
    result = calc.calculate_income_amount(
        income=income,
        year=2025,  # Age 55
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert not result.is_active
    assert result.adjusted_amount == Decimal('0')
    
    # At retirement age
    result = calc.calculate_income_amount(
        income=income,
        year=2037,  # Age 67
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert result.is_active
    assert result.adjusted_amount > Decimal('30000')  # Inflation adjusted

def test_multiple_income_stream_interactions():
    """Test interactions between multiple retirement income streams."""
    calc = RetirementIncomeCalculator()
    
    # Create multiple income streams with different characteristics
    incomes = [
        RetirementIncomePlan(
            name="Social Security",
            owner="person1",
            annual_income=Decimal('30000'),
            start_age=67,
            income_type=RetirementIncomeType.SOCIAL_SECURITY,
            dob=date(1970, 1, 1),
            apply_inflation=True
        ),
        RetirementIncomePlan(
            name="Pension",
            owner="person1",
            annual_income=Decimal('40000'),
            start_age=65,
            income_type=RetirementIncomeType.PENSION,
            dob=date(1970, 1, 1),
            apply_inflation=False
        ),
        RetirementIncomePlan(
            name="Part-time Work",
            owner="person1",
            annual_income=Decimal('20000'),
            start_age=65,
            end_age=70,
            income_type=RetirementIncomeType.OTHER,
            dob=date(1970, 1, 1),
            apply_inflation=True
        )
    ]
    
    # Test before any income starts (age 60)
    results = calc.calculate_multiple_income_streams(
        income_streams=incomes,
        year=2030,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert sum(r.adjusted_amount for r in results) == Decimal('0')
    
    # Test when pension and part-time work active (age 65)
    results = calc.calculate_multiple_income_streams(
        income_streams=incomes,
        year=2035,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    active_results = [r for r in results if r.is_active]
    assert len(active_results) == 2
    
    # Test when all income streams active (age 67)
    results = calc.calculate_multiple_income_streams(
        income_streams=incomes,
        year=2037,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    active_results = [r for r in results if r.is_active]
    assert len(active_results) == 3
    
    # Test after part-time work ends (age 71)
    results = calc.calculate_multiple_income_streams(
        income_streams=incomes,
        year=2041,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    active_results = [r for r in results if r.is_active]
    assert len(active_results) == 2

def test_long_term_inflation_impact():
    """Test long-term inflation effects on retirement income."""
    calc = RetirementIncomeCalculator()
    
    # Test income with inflation adjustment
    income_with_inflation = RetirementIncomePlan(
        name="Social Security",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=67,
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    # Test income without inflation adjustment
    income_without_inflation = RetirementIncomePlan(
        name="Fixed Pension",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=67,
        dob=date(1970, 1, 1),
        apply_inflation=False
    )
    
    # Calculate values after 30 years of inflation
    start_year = 2037  # Retirement year
    end_year = 2067    # 30 years later
    inflation_rate = Decimal('0.03')
    
    # With inflation
    result_with_inflation = calc.calculate_income_amount(
        income=income_with_inflation,
        year=end_year,
        inflation_rate=inflation_rate,
        plan_start_year=start_year
    )
    
    # Without inflation
    result_without_inflation = calc.calculate_income_amount(
        income=income_without_inflation,
        year=end_year,
        inflation_rate=inflation_rate,
        plan_start_year=start_year
    )
    
    # Verify inflation impact
    assert result_with_inflation.adjusted_amount > result_without_inflation.adjusted_amount
    expected_with_inflation = Decimal('30000') * (1 + inflation_rate) ** 30
    assert abs(result_with_inflation.adjusted_amount - expected_with_inflation) < Decimal('0.01')

def test_retirement_income_edge_cases():
    """Test edge cases in retirement income calculations."""
    calc = RetirementIncomeCalculator()
    
    # Test income starting exactly at plan start
    immediate_income = RetirementIncomePlan(
        name="Immediate Income",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=55,  # Current age
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    result = calc.calculate_income_amount(
        income=immediate_income,
        year=2025,  # Plan start year
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert result.is_active
    assert result.adjusted_amount == Decimal('30000')
    
    # Test income with maximum age
    max_age_income = RetirementIncomePlan(
        name="Max Age Test",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=65,
        end_age=120,  # Maximum age
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    # Test at age 119
    result = calc.calculate_income_amount(
        income=max_age_income,
        year=2089,  # Age 119
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert result.is_active
    
    # Test at age 121
    result = calc.calculate_income_amount(
        income=max_age_income,
        year=2091,  # Age 121
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    assert not result.is_active

def test_income_type_specific_calculations():
    """Test calculations specific to different income types."""
    calc = RetirementIncomeCalculator()
    
    # Test Social Security with special inflation rules
    social_security = RetirementIncomePlan(
        name="Social Security",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=67,
        income_type=RetirementIncomeType.SOCIAL_SECURITY,
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    # Test pension with no inflation
    pension = RetirementIncomePlan(
        name="Pension",
        owner="person1",
        annual_income=Decimal('40000'),
        start_age=65,
        income_type=RetirementIncomeType.PENSION,
        dob=date(1970, 1, 1),
        apply_inflation=False
    )
    
    # Calculate and compare different income types
    year = 2037  # When both are active
    
    ss_result = calc.calculate_income_amount(
        income=social_security,
        year=year,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    pension_result = calc.calculate_income_amount(
        income=pension,
        year=year,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    assert ss_result.is_active
    assert pension_result.is_active
    assert ss_result.income_type == RetirementIncomeType.SOCIAL_SECURITY
    assert pension_result.income_type == RetirementIncomeType.PENSION

def test_partial_year_activation():
    """Test retirement income activation for partial years."""
    calc = RetirementIncomeCalculator()
    
    # Test mid-year birthday activation
    mid_year_income = RetirementIncomePlan(
        name="Mid-Year Test",
        owner="person1",
        annual_income=Decimal('30000'),
        start_age=65,
        dob=date(1970, 6, 15),  # Mid-year birthday
        apply_inflation=True
    )
    
    # Test exact activation year
    activation_year = get_year_for_age(mid_year_income.dob, mid_year_income.start_age)
    
    result = calc.calculate_income_amount(
        income=mid_year_income,
        year=activation_year,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    assert result.is_active
    assert result.partial_year_factor == Decimal('0.5')  # Half year
    assert result.adjusted_amount == Decimal('15000')  # Half of annual amount

def test_income_calculation_precision():
    """Test precision handling in income calculations."""
    calc = RetirementIncomeCalculator()
    
    # Test precise income amounts
    precise_income = RetirementIncomePlan(
        name="Precise Test",
        owner="person1",
        annual_income=Decimal('30123.45'),
        start_age=65,
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    result = calc.calculate_income_amount(
        income=precise_income,
        year=2035,
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    # Verify precision maintained
    assert isinstance(result.adjusted_amount, Decimal)
    assert result.adjusted_amount.as_tuple().exponent <= -2  # At least 2 decimal places