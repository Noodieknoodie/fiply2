# tests/conftest.py
import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database_operations.models import Base, Household, Plan, BaseAssumption
from database_operations.connection import get_session

@pytest.fixture
def engine():
    """Create test database in memory."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    """Creates a fresh test database session."""
    with Session(engine) as session:
        yield session
        session.rollback()

@pytest.fixture
def base_household(db_session):
    """Creates a test household with one person."""
    household = Household(
        household_name="Test Household",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1970, 1, 1)
    )
    db_session.add(household)
    db_session.commit()
    return household

@pytest.fixture
def base_plan(db_session, base_household):
    """Creates a test plan with basic assumptions."""
    plan = Plan(
        household_id=base_household.household_id,
        plan_name="Test Plan",
        plan_creation_year=datetime.now().year
    )
    db_session.add(plan)
    db_session.flush()

    assumptions = BaseAssumption(
        plan_id=plan.plan_id,
        retirement_age_1=65,
        final_age_1=95,
        default_growth_rate=Decimal('0.06'),
        inflation_rate=Decimal('0.03')
    )
    db_session.add(assumptions)
    db_session.commit()
    return plan


@pytest.fixture
def base_plan_with_facts(db_session, base_plan):
    """Creates a plan with sample assets, liabilities, and cash flows."""
    from database_operations.models import (
        AssetCategory, Asset, LiabilityCategory, Liability,
        InflowOutflow, RetirementIncomePlan
    )
    
    # Categories
    asset_cat = AssetCategory(
        plan_id=base_plan.plan_id,
        category_name="Retirement Accounts"
    )
    db_session.add(asset_cat)

    liability_cat = LiabilityCategory(
        plan_id=base_plan.plan_id,
        category_name="Mortgages"
    )
    db_session.add(liability_cat)
    db_session.flush()

    # Typical retirement portfolio components
    asset = Asset(
        plan_id=base_plan.plan_id,
        asset_category_id=asset_cat.asset_category_id,
        asset_name="401(k)",
        owner="person1",
        value=500000.00,
        include_in_nest_egg=True
    )
    db_session.add(asset)

    asset2 = Asset(
        plan_id=base_plan.plan_id,
        asset_category_id=asset_cat.asset_category_id,
        asset_name="House",
        owner="joint",
        value=400000.00,
        include_in_nest_egg=False  # Non-retirement asset
    )
    db_session.add(asset2)

    liability = Liability(
        plan_id=base_plan.plan_id,
        liability_category_id=liability_cat.liability_category_id,
        liability_name="Mortgage",
        owner="joint",
        value=300000.00,
        interest_rate=0.0375,
        include_in_nest_egg=True
    )
    db_session.add(liability)

    # Regular cash flows
    salary = InflowOutflow(
        plan_id=base_plan.plan_id,
        type="inflow",
        name="Salary",
        owner="person1",
        annual_amount=100000.00,
        start_year=base_plan.plan_creation_year,
        end_year=base_plan.plan_creation_year + 10,
        apply_inflation=True
    )
    db_session.add(salary)

    # Retirement income at retirement age
    social_security = RetirementIncomePlan(
        plan_id=base_plan.plan_id,
        name="Social Security",
        owner="person1",
        annual_income=30000.00,
        start_age=67,
        apply_inflation=True
    )
    db_session.add(social_security)

    db_session.commit()
    return base_plan