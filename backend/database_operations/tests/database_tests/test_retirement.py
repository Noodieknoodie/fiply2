"""Tests for retirement income plans CRUD operations."""

from datetime import date
import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..models import Base, Household, Plan, RetirementIncomePlan
from ..crud.financial.retirement import (
    RetirementIncomePlanCreate,
    RetirementIncomePlanUpdate,
    create_retirement_plan,
    get_retirement_plan,
    get_plan_retirement_plans,
    update_retirement_plan,
    delete_retirement_plan
)

@pytest.fixture(autouse=True)
def cleanup_database(db_session: Session):
    """Cleanup the database before each test."""
    try:
        db_session.execute(delete(RetirementIncomePlan))
        db_session.execute(delete(Plan))
        db_session.execute(delete(Household))
        Base.metadata.drop_all(bind=db_session.get_bind())
        Base.metadata.create_all(bind=db_session.get_bind())
        yield
    finally:
        db_session.rollback()

@pytest.fixture
def sample_household(db_session: Session) -> Household:
    """Create a sample household."""
    try:
        household = Household(
            household_name="Test Household",
            person1_first_name="John",
            person1_last_name="Doe",
            person1_dob=date(1990, 1, 1)
        )
        db_session.add(household)
        db_session.flush()
        return household
    except Exception:
        db_session.rollback()
        raise

@pytest.fixture
def sample_plan(db_session: Session, sample_household: Household) -> Plan:
    """Create a sample plan."""
    try:
        plan = Plan(
            household_id=sample_household.household_id,
            plan_name="Test Plan",
            description="Test Description",
            is_active=True
        )
        db_session.add(plan)
        db_session.flush()
        return plan
    except Exception:
        db_session.rollback()
        raise

@pytest.fixture
def sample_retirement_data(sample_plan: Plan) -> RetirementIncomePlanCreate:
    """Create sample retirement income plan data."""
    return RetirementIncomePlanCreate(
        plan_id=sample_plan.plan_id,
        name="Social Security",
        owner="person1",
        annual_income=30000.0,
        start_age=67,
        end_age=95,
        include_in_nest_egg=True,
        apply_inflation=True
    )

def test_create_retirement_plan(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test creating a retirement income plan."""
    try:
        retirement_plan = create_retirement_plan(db_session, sample_retirement_data)
        assert retirement_plan is not None
        assert retirement_plan.plan_id == sample_retirement_data.plan_id
        assert retirement_plan.name == "Social Security"
        assert retirement_plan.owner == "person1"
        assert retirement_plan.annual_income == 30000.0
        assert retirement_plan.start_age == 67
        assert retirement_plan.end_age == 95
        # SQLite stores booleans as integers
        assert retirement_plan.include_in_nest_egg == 1
        assert retirement_plan.apply_inflation == 1
    finally:
        db_session.rollback()

def test_create_retirement_plan_invalid_plan(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test creating a retirement income plan with invalid plan ID."""
    try:
        invalid_data = RetirementIncomePlanCreate(**vars(sample_retirement_data))
        invalid_data.plan_id = 999
        retirement_plan = create_retirement_plan(db_session, invalid_data)
        assert retirement_plan is None
    finally:
        db_session.rollback()

def test_get_retirement_plan(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test retrieving a retirement income plan."""
    try:
        created = create_retirement_plan(db_session, sample_retirement_data)
        assert created is not None
        
        retrieved = get_retirement_plan(db_session, created.income_plan_id)
        assert retrieved is not None
        assert retrieved.name == "Social Security"
        assert retrieved.annual_income == 30000.0
        assert retrieved.apply_inflation == 1
        # Verify plan relationship is loaded
        assert retrieved.plan is not None
        assert retrieved.plan.plan_id == sample_retirement_data.plan_id
    finally:
        db_session.rollback()

def test_get_nonexistent_retirement_plan(db_session: Session):
    """Test retrieving a non-existent retirement income plan."""
    try:
        retrieved = get_retirement_plan(db_session, 999)
        assert retrieved is None
    finally:
        db_session.rollback()

def test_get_plan_retirement_plans(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test retrieving all retirement income plans for a plan."""
    try:
        # Create first retirement plan
        created_ss = create_retirement_plan(db_session, sample_retirement_data)
        assert created_ss is not None
        
        # Create second retirement plan
        pension_data = RetirementIncomePlanCreate(
            plan_id=sample_retirement_data.plan_id,
            name="Pension",
            owner="person1",
            annual_income=40000.0,
            start_age=65,
            apply_inflation=False
        )
        created_pension = create_retirement_plan(db_session, pension_data)
        assert created_pension is not None
        
        # Test getting all retirement plans
        all_plans = get_plan_retirement_plans(db_session, sample_retirement_data.plan_id)
        assert len(all_plans) == 2
        assert any(plan.name == "Social Security" and plan.apply_inflation == 1 for plan in all_plans)
        assert any(plan.name == "Pension" and plan.apply_inflation == 0 for plan in all_plans)
    finally:
        db_session.rollback()

def test_update_retirement_plan(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test updating a retirement income plan."""
    try:
        retirement_plan = create_retirement_plan(db_session, sample_retirement_data)
        assert retirement_plan is not None
        
        update_data = RetirementIncomePlanUpdate(
            name="Updated Social Security",
            annual_income=32000.0,
            include_in_nest_egg=False,
            apply_inflation=False
        )
        
        updated = update_retirement_plan(db_session, retirement_plan.income_plan_id, update_data)
        assert updated is not None
        assert updated.name == "Updated Social Security"
        assert updated.annual_income == 32000.0
        # SQLite stores booleans as integers
        assert updated.include_in_nest_egg == 0
        assert updated.apply_inflation == 0
        # Unchanged fields should remain the same
        assert updated.start_age == 67
        assert updated.end_age == 95
    finally:
        db_session.rollback()

def test_update_nonexistent_retirement_plan(db_session: Session):
    """Test updating a non-existent retirement income plan."""
    try:
        update_data = RetirementIncomePlanUpdate(name="Updated Name")
        updated = update_retirement_plan(db_session, 999, update_data)
        assert updated is None
    finally:
        db_session.rollback()

def test_delete_retirement_plan(db_session: Session, sample_retirement_data: RetirementIncomePlanCreate):
    """Test deleting a retirement income plan."""
    try:
        retirement_plan = create_retirement_plan(db_session, sample_retirement_data)
        assert retirement_plan is not None
        
        assert delete_retirement_plan(db_session, retirement_plan.income_plan_id) == True
        assert get_retirement_plan(db_session, retirement_plan.income_plan_id) is None
    finally:
        db_session.rollback()

def test_delete_nonexistent_retirement_plan(db_session: Session):
    """Test deleting a non-existent retirement income plan."""
    try:
        assert delete_retirement_plan(db_session, 999) == False
    finally:
        db_session.rollback() 