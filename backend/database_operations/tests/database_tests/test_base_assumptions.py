from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from database_operations.models import Plan, Household, BaseAssumption, Base
from database_operations.connection import get_session
from database_operations.crud.base_assumptions import (
    BaseAssumptionCreate,
    BaseAssumptionUpdate,
    create_base_assumption,
    get_base_assumption,
    update_base_assumption,
    delete_base_assumption
)
from database_operations.crud.plans import PlanCreate, create_plan
from database_operations.crud.households import HouseholdCreate, create_household

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
    """Create a sample household for testing."""
    household_data = HouseholdCreate(
        household_name="Test Family",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1980, 1, 1)
    )
    return create_household(db_session, household_data)

@pytest.fixture
def sample_plan(db_session: Session, sample_household: Household):
    """Create a sample plan for testing."""
    plan_data = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Test Plan"
    )
    return create_plan(db_session, plan_data)

@pytest.fixture
def sample_assumptions_data(sample_plan: Plan):
    """Create sample base assumptions data."""
    return BaseAssumptionCreate(
        plan_id=sample_plan.plan_id,
        retirement_age_1=65,
        retirement_age_2=62,
        final_age_1=95,
        final_age_2=92,
        final_age_selector=1,
        default_growth_rate=0.07,
        inflation_rate=0.03
    )

def test_create_base_assumptions(db_session: Session, sample_assumptions_data: BaseAssumptionCreate):
    """Test creating base assumptions."""
    assumptions = create_base_assumption(db_session, sample_assumptions_data)
    
    assert assumptions.plan_id == sample_assumptions_data.plan_id
    assert assumptions.retirement_age_1 == 65
    assert assumptions.retirement_age_2 == 62
    assert assumptions.final_age_1 == 95
    assert assumptions.final_age_2 == 92
    assert assumptions.final_age_selector == 1
    assert assumptions.default_growth_rate == 0.07
    assert assumptions.inflation_rate == 0.03

def test_get_plan_assumptions(db_session: Session, sample_assumptions_data: BaseAssumptionCreate):
    """Test retrieving base assumptions for a plan."""
    created_assumptions = create_base_assumption(db_session, sample_assumptions_data)
    retrieved_assumptions = get_base_assumption(db_session, created_assumptions.plan_id)
    
    assert retrieved_assumptions is not None
    assert retrieved_assumptions.plan_id == created_assumptions.plan_id
    assert retrieved_assumptions.retirement_age_1 == created_assumptions.retirement_age_1

def test_get_nonexistent_assumptions(db_session: Session):
    """Test retrieving assumptions for a non-existent plan."""
    assumptions = get_base_assumption(db_session, 999)
    assert assumptions is None

def test_update_base_assumptions(db_session: Session, sample_assumptions_data: BaseAssumptionCreate):
    """Test updating base assumptions."""
    assumptions = create_base_assumption(db_session, sample_assumptions_data)
    
    update_data = BaseAssumptionUpdate(
        retirement_age_1=67,
        default_growth_rate=0.08
    )
    
    updated_assumptions = update_base_assumption(db_session, assumptions.plan_id, update_data)
    assert updated_assumptions is not None
    assert updated_assumptions.retirement_age_1 == 67
    assert updated_assumptions.default_growth_rate == 0.08
    # Other fields should remain unchanged
    assert updated_assumptions.retirement_age_2 == 62
    assert updated_assumptions.final_age_1 == 95

def test_update_nonexistent_assumptions(db_session: Session):
    """Test updating non-existent assumptions."""
    update_data = BaseAssumptionUpdate(retirement_age_1=67)
    updated_assumptions = update_base_assumption(db_session, 999, update_data)
    assert updated_assumptions is None

def test_delete_base_assumptions(db_session: Session, sample_assumptions_data: BaseAssumptionCreate):
    """Test deleting base assumptions."""
    assumptions = create_base_assumption(db_session, sample_assumptions_data)
    
    assert delete_base_assumption(db_session, assumptions.plan_id) is True
    assert get_base_assumption(db_session, assumptions.plan_id) is None

def test_delete_nonexistent_assumptions(db_session: Session):
    """Test deleting non-existent assumptions."""
    assert delete_base_assumption(db_session, 999) is False 