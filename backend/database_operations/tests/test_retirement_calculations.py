# tests/test_retirement_calculations.py
from decimal import Decimal
from datetime import date
import pytest
from database_operations.calculations.base_facts.retirement_income_calcs import RetirementIncomeCalculator
from database_operations.models import RetirementIncomePlan

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

def test_inflation_adjustments():
    """Test inflation adjustments on retirement income."""
    calc = RetirementIncomeCalculator()
    
    income = RetirementIncomePlan(
        name="Pension",
        owner="person1",
        annual_income=Decimal('50000'),
        start_age=65,
        dob=date(1970, 1, 1),
        apply_inflation=True
    )
    
    # Calculate after 10 years of inflation
    result = calc.calculate_income_amount(
        income=income,
        year=2035,  # Age 65
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    expected = Decimal('50000') * (Decimal('1.03') ** 10)
    assert abs(result.adjusted_amount - expected) < Decimal('0.01')

def test_retirement_income_aggregation():
    """Test aggregation of multiple retirement income streams."""
    calc = RetirementIncomeCalculator()
    
    incomes = [
        RetirementIncomePlan(
            name="Social Security",
            owner="person1",
            annual_income=Decimal('30000'),
            start_age=67,
            dob=date(1970, 1, 1)
        ),
        RetirementIncomePlan(
            name="Pension",
            owner="person1",
            annual_income=Decimal('40000'),
            start_age=65,
            dob=date(1970, 1, 1)
        )
    ]
    
    results = calc.calculate_multiple_income_streams(
        income_streams=incomes,
        year=2037,  # Age 67 - both should be active
        inflation_rate=Decimal('0.03'),
        plan_start_year=2025
    )
    
    total = calc.calculate_total_income(results)
    assert total > Decimal('70000')  # Base amount plus inflation