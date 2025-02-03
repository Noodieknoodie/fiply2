# tests/test_scenario_creation.py
import pytest
from decimal import Decimal
from datetime import date
from database_operations.crud.scenarios_crud import ScenarioCRUD
from database_operations.models import (
    Asset, Liability, InflowOutflow, RetirementIncomePlan,
    GrowthRateConfiguration, ScenarioOverride
)

@pytest.fixture
def complex_base_plan(db_session, base_plan_with_facts):
    """Creates a plan with multiple assets, liabilities, and configurations."""
    # Add additional growth rate configurations
    growth_config = GrowthRateConfiguration(
        asset_id=1,  # From base_plan_with_facts
        configuration_type='STEPWISE',
        start_year=2025,
        end_year=2027,
        growth_rate=Decimal('0.08')
    )
    db_session.add(growth_config)
    
    # Add additional retirement income
    pension = RetirementIncomePlan(
        plan_id=base_plan_with_facts.plan_id,
        name="Private Pension",
        owner="person1",
        annual_income=Decimal('25000'),
        start_age=65,
        apply_inflation=True
    )
    db_session.add(pension)
    
    # Add more complex cash flows
    bonus = InflowOutflow(
        plan_id=base_plan_with_facts.plan_id,
        type="inflow",
        name="Annual Bonus",
        owner="person1",
        annual_amount=Decimal('10000'),
        start_year=2025,
        end_year=2035,
        apply_inflation=True
    )
    db_session.add(bonus)
    
    db_session.commit()
    return base_plan_with_facts

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

def test_complete_scenario_inheritance(db_session, complex_base_plan):
    """Test comprehensive inheritance of all plan components."""
    crud = ScenarioCRUD(db_session)
    
    # Create scenario with single asset override
    scenario = crud.create_scenario(
        plan_id=complex_base_plan.plan_id,
        scenario_name="Inheritance Test"
    )
    
    # Override single asset value
    asset_override = ScenarioOverride(
        scenario_id=scenario.scenario_id,
        target_type="asset",
        target_id=1,
        field="value",
        value=Decimal('600000')
    )
    db_session.add(asset_override)
    db_session.commit()
    
    # Verify all components
    scenario_details = crud.get_scenario_details(scenario.scenario_id)
    
    # Check assets inheritance
    assert len(scenario_details.assets) == len(complex_base_plan.assets)
    modified_asset = next(a for a in scenario_details.assets if a.asset_id == 1)
    assert modified_asset.value == Decimal('600000')
    
    # Check unmodified assets maintain original values
    unmodified_assets = [a for a in scenario_details.assets if a.asset_id != 1]
    for asset in unmodified_assets:
        base_asset = next(a for a in complex_base_plan.assets if a.asset_id == asset.asset_id)
        assert asset.value == base_asset.value
    
    # Verify growth rate configurations inheritance
    assert len(scenario_details.growth_configurations) == len(complex_base_plan.growth_configurations)
    
    # Check liabilities inheritance
    assert len(scenario_details.liabilities) == len(complex_base_plan.liabilities)
    
    # Check cash flows inheritance
    assert len(scenario_details.cash_flows) == len(complex_base_plan.cash_flows)
    
    # Check retirement income inheritance
    assert len(scenario_details.retirement_income_plans) == len(complex_base_plan.retirement_income_plans)

def test_scenario_asset_inheritance(db_session, complex_base_plan):
    """Test detailed asset inheritance with growth configurations."""
    crud = ScenarioCRUD(db_session)
    
    # Create scenario with growth rate override
    scenario = crud.create_scenario(
        plan_id=complex_base_plan.plan_id,
        scenario_name="Asset Growth Test"
    )
    
    # Override growth rate configuration
    growth_override = ScenarioOverride(
        scenario_id=scenario.scenario_id,
        target_type="growth_rate",
        target_id=1,
        field="growth_rate",
        value=Decimal('0.09')
    )
    db_session.add(growth_override)
    db_session.commit()
    
    # Verify growth rate inheritance and override
    scenario_details = crud.get_scenario_details(scenario.scenario_id)
    modified_growth = next(
        g for g in scenario_details.growth_configurations 
        if g.asset_id == 1 and g.configuration_type == 'STEPWISE'
    )
    assert modified_growth.growth_rate == Decimal('0.09')
    
    # Verify other growth configurations remain unchanged
    unmodified_growth = [
        g for g in scenario_details.growth_configurations 
        if g.asset_id != 1 or g.configuration_type != 'STEPWISE'
    ]
    for growth in unmodified_growth:
        base_growth = next(
            g for g in complex_base_plan.growth_configurations 
            if g.asset_id == growth.asset_id
        )
        assert growth.growth_rate == base_growth.growth_rate

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
    
    # Should raise error for invalid target type
    with pytest.raises(ValueError, match="Invalid target type"):
        crud.add_override(
            scenario_id=scenario.scenario_id,
            target_type="invalid_type",
            target_id=1,
            override_field="value",
            override_value="100000"
        )
    
    # Should raise error for non-existent target
    with pytest.raises(ValueError, match="Target not found"):
        crud.add_override(
            scenario_id=scenario.scenario_id,
            target_type="asset",
            target_id=999,
            override_field="value",
            override_value="100000"
        )

def test_scenario_assumption_inheritance(db_session, complex_base_plan):
    """Test inheritance and override of scenario assumptions."""
    crud = ScenarioCRUD(db_session)
    
    # Create scenario with modified assumptions
    scenario = crud.create_scenario(
        plan_id=complex_base_plan.plan_id,
        scenario_name="Assumption Test",
        assumptions={
            'retirement_age_1': 67,
            'default_growth_rate': Decimal('0.07')
        }
    )
    
    # Verify modified assumptions
    scenario_assumptions = crud.get_scenario(
        scenario.scenario_id,
        include_assumptions=True
    ).assumptions
    
    assert scenario_assumptions.retirement_age_1 == 67
    assert scenario_assumptions.default_growth_rate == Decimal('0.07')
    
    # Verify unmodified assumptions match base plan
    assert scenario_assumptions.inflation_rate == complex_base_plan.base_assumptions.inflation_rate
    assert scenario_assumptions.final_age_1 == complex_base_plan.base_assumptions.final_age_1