from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from ..connection import get_session
from ..models import Plan, Household, Base
from ..crud.plans import (
    PlanCreate,
    PlanUpdate,
    create_plan,
    get_plan,
    get_household_plans,
    update_plan,
    delete_plan
)
from ..crud.households import HouseholdCreate, create_household

@pytest.fixture(autouse=True)
def cleanup_database():
    """Cleanup the database before each test."""
    session = get_session()
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=session.get_bind())
        # Recreate all tables with current schema
        Base.metadata.create_all(bind=session.get_bind())
        session.commit()
    finally:
        session.close()

@pytest.fixture
def db_session():
    """Fixture that provides a database session."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_household(db_session: Session):
    """Fixture that creates and returns a sample household."""
    household_data = HouseholdCreate(
        household_name="Test Family",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1980, 1, 1)
    )
    return create_household(db_session, household_data)

@pytest.fixture
def sample_plan_data(sample_household: Household):
    """Fixture that provides sample plan data."""
    return PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Test Plan",
        description="A test financial plan",
        target_fire_age=55,
        target_fire_amount=1000000.0,
        risk_tolerance="Moderate"
    )

def test_create_plan(db_session: Session, sample_plan_data: PlanCreate):
    """Test creating a plan."""
    plan = create_plan(db_session, sample_plan_data)
    
    assert plan.plan_name == "Test Plan"
    assert plan.description == "A test financial plan"
    assert plan.target_fire_age == 55
    assert plan.target_fire_amount == 1000000.0
    assert plan.risk_tolerance == "Moderate"
    assert plan.is_active is True
    assert plan.plan_id is not None

def test_get_plan(db_session: Session, sample_plan_data: PlanCreate):
    """Test retrieving a plan by ID."""
    created_plan = create_plan(db_session, sample_plan_data)
    retrieved_plan = get_plan(db_session, created_plan.plan_id)
    
    assert retrieved_plan is not None
    assert retrieved_plan.plan_id == created_plan.plan_id
    assert retrieved_plan.plan_name == created_plan.plan_name

def test_get_nonexistent_plan(db_session: Session):
    """Test retrieving a non-existent plan."""
    plan = get_plan(db_session, 999)
    assert plan is None

def test_get_household_plans(db_session: Session, sample_household: Household):
    """Test retrieving all plans for a household."""
    # Create multiple plans
    plan_data1 = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Plan 1"
    )
    plan_data2 = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Plan 2"
    )
    
    create_plan(db_session, plan_data1)
    create_plan(db_session, plan_data2)
    
    plans = get_household_plans(db_session, sample_household.household_id)
    assert len(plans) == 2
    assert all(plan.household_id == sample_household.household_id for plan in plans)

def test_update_plan(db_session: Session, sample_plan_data: PlanCreate):
    """Test updating a plan."""
    plan = create_plan(db_session, sample_plan_data)
    
    update_data = PlanUpdate(
        plan_name="Updated Plan",
        target_fire_age=60,
        risk_tolerance="Conservative"
    )
    
    updated_plan = update_plan(db_session, plan.plan_id, update_data)
    assert updated_plan is not None
    assert updated_plan.plan_name == "Updated Plan"
    assert updated_plan.target_fire_age == 60
    assert updated_plan.risk_tolerance == "Conservative"
    # Unchanged fields should remain the same
    assert updated_plan.target_fire_amount == 1000000.0

def test_update_nonexistent_plan(db_session: Session):
    """Test updating a non-existent plan."""
    update_data = PlanUpdate(plan_name="Updated Plan")
    updated_plan = update_plan(db_session, 999, update_data)
    assert updated_plan is None

def test_delete_plan(db_session: Session, sample_plan_data: PlanCreate):
    """Test deleting a plan."""
    plan = create_plan(db_session, sample_plan_data)
    
    assert delete_plan(db_session, plan.plan_id) is True
    assert get_plan(db_session, plan.plan_id) is None

def test_delete_nonexistent_plan(db_session: Session):
    """Test deleting a non-existent plan."""
    assert delete_plan(db_session, 999) is False

def test_get_household_plans_with_inactive(db_session: Session, sample_household: Household):
    """Test retrieving plans including inactive ones."""
    # Create one active and one inactive plan
    plan_data1 = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Active Plan"
    )
    plan_data2 = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Inactive Plan"
    )
    
    plan1 = create_plan(db_session, plan_data1)
    plan2 = create_plan(db_session, plan_data2)
    
    # Make plan2 inactive
    update_plan(db_session, plan2.plan_id, PlanUpdate(is_active=False))
    
    # Test without inactive plans
    active_plans = get_household_plans(db_session, sample_household.household_id)
    assert len(active_plans) == 1
    assert active_plans[0].plan_name == "Active Plan"
    
    # Test with inactive plans
    all_plans = get_household_plans(
        db_session, 
        sample_household.household_id, 
        include_inactive=True
    )
    assert len(all_plans) == 2 