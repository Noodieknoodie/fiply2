# backend\database_operations\tests\test_connection.py

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy import inspect
from datetime import date, datetime

from database_operations.connection import get_engine, get_session
from database_operations.models import (
    Base, Household, Plan, BaseAssumption, Scenario, ScenarioAssumption,
    ScenarioOverride, AssetCategory, Asset, LiabilityCategory, Liability,
    InflowOutflow, RetirementIncomePlan, GrowthRateConfiguration
)

def test_database_connection():
    """Test that we can connect to the database and create tables."""
    engine = get_engine()
    inspector = inspect(engine)
    
    # Verify all tables were created
    expected_tables = {
        'households',
        'plans',
        'base_assumptions',
        'scenarios',
        'scenario_assumptions',
        'scenario_overrides',
        'asset_categories',
        'assets',
        'liability_categories',
        'liabilities',
        'inflows_outflows',
        'retirement_income_plans',
        'growth_rate_configurations'
    }
    
    actual_tables = set(inspector.get_table_names())
    assert expected_tables.issubset(actual_tables), \
        f"Missing tables: {expected_tables - actual_tables}"

def test_create_household_with_plan():
    """Test creating a household with a basic plan."""
    session = get_session()
    
    try:
        # Create a test household
        household = Household(
            household_name="Test Family",
            person1_first_name="John",
            person1_last_name="Doe",
            person1_dob=date(1980, 1, 1)
        )
        session.add(household)
        session.flush()
        
        # Create a plan for the household
        plan = Plan(
            household_id=household.household_id,
            plan_name="Test Plan"
        )
        session.add(plan)
        session.flush()
        
        # Add base assumptions and establish relationship
        assumptions = BaseAssumption(
            plan_id=plan.plan_id,
            retirement_age_1=65,
            final_age_1=95,
            default_growth_rate=0.06,
            inflation_rate=0.03
        )
        session.add(assumptions)
        session.flush()  # Flush to establish relationship
        
        # Refresh plan to see the new relationship
        session.refresh(plan)
        
        # Verify the relationships
        assert len(household.plans) == 1
        assert household.plans[0].plan_name == "Test Plan"
        assert household.plans[0].base_assumptions.retirement_age_1 == 65
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def test_create_complete_financial_plan():
    """Test creating a plan with assets, liabilities, and scenarios."""
    session = get_session()
    
    try:
        # Create base household and plan
        household = Household(
            household_name="Complete Test Family",
            person1_first_name="Jane",
            person1_last_name="Smith",
            person1_dob=date(1975, 6, 15)
        )
        session.add(household)
        session.flush()
        
        plan = Plan(
            household_id=household.household_id,
            plan_name="Complete Test Plan"
        )
        session.add(plan)
        session.flush()
        
        # Create asset category and asset
        asset_category = AssetCategory(
            plan_id=plan.plan_id,
            category_name="Retirement Accounts"
        )
        session.add(asset_category)
        session.flush()
        
        asset = Asset(
            plan_id=plan.plan_id,
            asset_category_id=asset_category.asset_category_id,
            asset_name="401(k)",
            owner="person1",
            value=500000.00
        )
        session.add(asset)
        session.flush()
        
        # Create scenario
        scenario = Scenario(
            plan_id=plan.plan_id,
            scenario_name="Early Retirement"
        )
        session.add(scenario)
        session.flush()
        
        # Add scenario assumption
        scenario_assumption = ScenarioAssumption(
            scenario_id=scenario.scenario_id,
            retirement_age_1=60,
            annual_retirement_spending=75000.00
        )
        session.add(scenario_assumption)
        session.flush()  # Flush to establish relationship
        
        # Add growth rate configuration
        growth_rate = GrowthRateConfiguration(
            asset_id=asset.asset_id,
            configuration_type="DEFAULT",
            growth_rate=0.07
        )
        session.add(growth_rate)
        session.flush()
        
        # Refresh objects to see new relationships
        session.refresh(plan)
        session.refresh(scenario)
        
        # Verify the relationships
        assert len(plan.assets) == 1
        assert plan.assets[0].value == 500000.00
        assert len(plan.scenarios) == 1
        assert plan.scenarios[0].assumptions.retirement_age_1 == 60
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()