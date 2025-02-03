# tests/test_scenario_creation.py
import pytest
from decimal import Decimal
from database_operations.crud.scenarios_crud import ScenarioCRUD

def test_create_basic_scenario(db_session, base_plan):
    """Test basic scenario creation with assumption inheritance."""
    crud = ScenarioCRUD(db_session)
    
    scenario = crud.create_scenario(
        plan_id=base_plan.plan_id,
        scenario_name="Test Scenario"
    )
    
    # Verify scenario creation
    assert scenario is not None
    assert scenario.plan_id == base_plan.plan_id
    
    # Verify assumption inheritance
    scenario_with_assumptions = crud.get_scenario(
        scenario.scenario_id, 
        include_assumptions=True
    )
    assert scenario_with_assumptions.assumptions is not None
    assert scenario_with_assumptions.assumptions.retirement_age_1 == base_plan.base_assumptions.retirement_age_1
    assert scenario_with_assumptions.assumptions.default_growth_rate == base_plan.base_assumptions.default_growth_rate

def test_create_scenario_with_retirement_spending(db_session, base_plan):
    """Test scenario creation with retirement spending."""
    crud = ScenarioCRUD(db_session)
    
    scenario = crud.create_scenario(
        plan_id=base_plan.plan_id,
        scenario_name="Retirement Test",
        assumptions={
            'annual_retirement_spending': Decimal('50000')
        }
    )
    
    scenario_assumptions = crud.get_scenario(
        scenario.scenario_id, 
        include_assumptions=True
    ).assumptions
    
    assert scenario_assumptions.annual_retirement_spending == Decimal('50000')
    
def test_scenario_override_validation(db_session, base_plan):
    """Test that scenario overrides are properly validated."""
    crud = ScenarioCRUD(db_session)
    
    scenario = crud.create_scenario(
        plan_id=base_plan.plan_id,
        scenario_name="Override Test"
    )
    
    # Should raise error when no target specified
    with pytest.raises(ValueError, match="Override must have a valid target"):
        crud.add_override(
            scenario_id=scenario.scenario_id,
            override_field="value",
            override_value="100000"
        )