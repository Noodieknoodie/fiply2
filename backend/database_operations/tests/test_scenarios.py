# tests/test_scenarios.py
from database_operations.models import BaseAssumption, Scenario, ScenarioAssumption

def test_scenario_inheritance(db_session, basic_plan):
    """Test scenario properly inherits base facts"""
    # Create base assumptions

    base = BaseAssumption(
        plan_id=basic_plan.id,
        retirement_age_1=65,
        final_age_1=95,
        default_growth_rate=0.06,
        inflation_rate=0.03
    )
    db_session.add(base)
    db_session.commit()
    
    # Create scenario
    scenario = Scenario(
        plan_id=basic_plan.id,
        scenario_name='Early Retirement'
    )
    db_session.add(scenario)
    db_session.commit()
    
    # Create scenario assumptions
    scenario_assumptions = ScenarioAssumption(
        scenario_id=scenario.id,
        retirement_age_1=60,  # Override retirement age
        annual_retirement_spending=85000.0
    )
    db_session.add(scenario_assumptions)
    db_session.commit()
    
    # Verify inheritance
    assert scenario_assumptions.retirement_age_1 == 60  # Overridden
    assert scenario_assumptions.inflation_rate == base.inflation_rate  # Inherited
