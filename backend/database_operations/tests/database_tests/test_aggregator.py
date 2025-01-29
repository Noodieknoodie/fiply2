"""Tests for the aggregator module."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from ...calculations.base_facts import aggregator
from ...calculations.base_facts import assets as asset_calc
from ...calculations.base_facts import liabilities as liability_calc
from ...calculations.base_facts import inflows_outflows as flow_calc
from ...calculations.base_facts import retirement_income as retirement_calc
from ...utils.money_utils import to_decimal, to_float

@pytest.fixture
def base_date() -> date:
    """Fixed base date for tests."""
    return date(2024, 1, 1)

@pytest.fixture
def test_assets() -> List[asset_calc.AssetFact]:
    """Sample assets for testing."""
    return [
        asset_calc.AssetFact(
            value=100000.0,
            owner=asset_calc.OwnerType.PERSON_1,
            include_in_nest_egg=True,
            category_id=1,
            name="Investment Account",
            growth_config=asset_calc.GrowthConfig(
                rate=0.07,
                config_type=asset_calc.GrowthType.OVERRIDE,
                time_range=asset_calc.TimeRange(
                    start_date=date(2024, 1, 1),
                    end_date=None
                )
            )
        ),
        asset_calc.AssetFact(
            value=500000.0,
            owner=asset_calc.OwnerType.JOINT,
            include_in_nest_egg=False,  # House not in nest egg
            category_id=2,
            name="Primary Home",
            growth_config=asset_calc.GrowthConfig(
                rate=0.03,
                config_type=asset_calc.GrowthType.OVERRIDE,
                time_range=asset_calc.TimeRange(
                    start_date=date(2024, 1, 1),
                    end_date=None
                )
            )
        )
    ]

@pytest.fixture
def test_liabilities() -> List[liability_calc.LiabilityFact]:
    """Sample liabilities for testing."""
    return [
        liability_calc.LiabilityFact(
            value=300000.0,
            owner=liability_calc.OwnerType.JOINT,
            include_in_nest_egg=False,  # Mortgage not in nest egg
            category_id=1,
            name="Mortgage",
            interest_rate=0.04
        ),
        liability_calc.LiabilityFact(
            value=10000.0,
            owner=liability_calc.OwnerType.PERSON_1,
            include_in_nest_egg=True,
            category_id=2,
            name="Investment Loan",
            interest_rate=0.05
        )
    ]

@pytest.fixture
def test_cash_flows() -> List[flow_calc.CashFlowFact]:
    """Sample cash flows for testing."""
    return [
        flow_calc.CashFlowFact(
            annual_amount=120000.0,
            type=flow_calc.FlowType.INFLOW,
            name="Salary",
            start_date=date(2024, 1, 1),
            end_date=date(2030, 12, 31),
            apply_inflation=True
        ),
        flow_calc.CashFlowFact(
            annual_amount=60000.0,
            type=flow_calc.FlowType.OUTFLOW,
            name="Living Expenses",
            start_date=date(2024, 1, 1),
            end_date=None,
            apply_inflation=True
        )
    ]

@pytest.fixture
def test_retirement_income() -> List[retirement_calc.RetirementIncomeFact]:
    """Sample retirement income for testing."""
    return [
        retirement_calc.RetirementIncomeFact(
            annual_income=40000.0,
            owner=retirement_calc.OwnerType.PERSON_1,
            include_in_nest_egg=True,
            name="Social Security",
            start_age=67,
            end_age=None,
            apply_inflation=True,
            person_dob=date(1980, 1, 1)
        )
    ]

@pytest.fixture
def test_base_facts(
    base_date,
    test_assets,
    test_liabilities,
    test_cash_flows,
    test_retirement_income
) -> aggregator.BaseFactsInput:
    """Complete base facts input for testing."""
    return aggregator.BaseFactsInput(
        assets=test_assets,
        liabilities=test_liabilities,
        cash_flows=test_cash_flows,
        retirement_income=test_retirement_income,
        default_growth_rate=0.05,
        inflation_rate=0.03,
        base_date=base_date,
        final_date=date(2026, 1, 1)  # 2 year projection
    )

def test_calculate_yearly_projection(test_base_facts, base_date):
    """Test calculation of financial projections for a specific year."""
    result = aggregator.calculate_yearly_projection(
        test_base_facts,
        base_date
    )
    
    # Verify structure and basic calculations
    assert result['year'] == 2024
    assert result['date'] == base_date
    
    # Verify assets
    assert result['assets']['total_assets'] > 600000  # Sum of both assets
    assert result['assets']['nest_egg_assets'] > 100000  # Only investment account
    
    # Verify liabilities
    assert result['liabilities']['total_liabilities'] > 310000  # Sum of both liabilities
    assert result['liabilities']['nest_egg_liabilities'] > 10000  # Only investment loan
    
    # Verify cash flows
    assert result['cash_flows']['total_inflows'] == 120000  # Salary
    assert result['cash_flows']['total_outflows'] == 60000  # Living expenses
    assert result['cash_flows']['net_cash_flow'] == 60000  # Net positive
    
    # Verify retirement income (not active yet at base date)
    assert result['retirement_income']['total_income'] == 0
    assert result['retirement_income']['nest_egg_income'] == 0
    
    # Verify portfolio calculations
    assert result['net_worth'] > 290000  # Total assets - Total liabilities
    assert result['retirement_portfolio'] > 90000  # Nest egg assets - Nest egg liabilities

def test_generate_projection_timeline(test_base_facts):
    """Test generation of year-by-year projections."""
    results = aggregator.generate_projection_timeline(test_base_facts)
    
    # Should have 3 years of projections (2024, 2025, 2026)
    assert len(results) == 3
    
    # Verify chronological order
    assert results[0]['year'] == 2024
    assert results[1]['year'] == 2025
    assert results[2]['year'] == 2026
    
    # Verify growth over time
    assert results[1]['assets']['total_assets'] > results[0]['assets']['total_assets']
    assert results[2]['assets']['total_assets'] > results[1]['assets']['total_assets']
    
    # Verify inflation on cash flows
    year_2_inflows = results[1]['cash_flows']['total_inflows']
    year_1_inflows = results[0]['cash_flows']['total_inflows']
    assert year_2_inflows > year_1_inflows  # Should increase with inflation

def test_retirement_portfolio_calculation(test_base_facts):
    """Test specific calculation of retirement portfolio values."""
    result = aggregator.calculate_yearly_projection(
        test_base_facts,
        test_base_facts.base_date
    )
    
    # Only investment account (100k) minus investment loan (10k)
    expected_min = 90000
    assert result['retirement_portfolio'] >= expected_min
    
    # House and mortgage should not affect retirement portfolio
    house_value = 500000
    mortgage_value = 300000
    total_non_nest_egg = house_value - mortgage_value
    
    # Difference between net worth and retirement portfolio should be non-nest egg value
    net_worth_retirement_diff = result['net_worth'] - result['retirement_portfolio']
    assert abs(net_worth_retirement_diff - total_non_nest_egg) < 1000  # Allow for rounding

def test_scenario_id_handling(test_base_facts):
    """Test that scenario ID is properly passed through to asset calculations."""
    # Calculate with and without scenario ID
    base_result = aggregator.calculate_yearly_projection(
        test_base_facts,
        test_base_facts.base_date
    )
    
    scenario_result = aggregator.calculate_yearly_projection(
        test_base_facts,
        test_base_facts.base_date,
        scenario_id=1
    )
    
    # Results should be the same since we haven't mocked scenario overrides
    assert base_result['assets']['total_assets'] == scenario_result['assets']['total_assets']
    assert base_result['retirement_portfolio'] == scenario_result['retirement_portfolio'] 