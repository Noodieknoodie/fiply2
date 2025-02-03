# tests/test_scenario_calculations.py
from decimal import Decimal
from database_operations.calculations.scenario_calcs import ScenarioCalculator
from database_operations.models import Scenario, ScenarioAssumption

def test_basic_scenario_calculation(db_session, base_plan_with_facts):
    """Test basic scenario calculation with retirement spending."""
    calc = ScenarioCalculator()
    
    # Create scenario with retirement spending
    scenario = Scenario(
        plan_id=base_plan_with_facts.plan_id,
        scenario_name="Test Scenario"
    )
    db_session.add(scenario)
    db_session.flush()
    
    # Add scenario assumptions
    assumptions = ScenarioAssumption(
        scenario_id=scenario.scenario_id,
        retirement_age_1=65,
        default_growth_rate=Decimal('0.06'),
        inflation_rate=Decimal('0.03'),
        annual_retirement_spending=Decimal('50000')
    )
    db_session.add(assumptions)
    db_session.commit()
    
    # Calculate one year
    year = base_plan_with_facts.plan_creation_year
    result = calc.calculate_scenario_year(
        scenario_id=scenario.scenario_id,
        year=year,
        prior_result=None
    )
    
    assert result is not None
    # No retirement spending yet (before retirement)
    assert result.retirement_spending == Decimal('0')
    
    # Verify portfolio values are calculated
    assert result.scenario_portfolio.asset_values is not None
    assert result.scenario_portfolio.liability_values is not None