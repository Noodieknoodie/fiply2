from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from ..models import Plan, Household, Scenario, ScenarioAssumption, Base
from ..connection import get_session
from ..crud.scenarios import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioAssumptionCreate,
    ScenarioAssumptionUpdate,
    create_scenario,
    get_scenario,
    get_plan_scenarios,
    update_scenario,
    delete_scenario,
    create_scenario_assumptions,
    get_scenario_assumptions,
    update_scenario_assumptions
)
from ..crud.plans import PlanCreate, create_plan
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
def sample_scenario_data(sample_plan: Plan):
    """Create sample scenario data."""
    return ScenarioCreate(
        plan_id=sample_plan.plan_id,
        scenario_name="Test Scenario",
        scenario_color="#FF0000"
    )

@pytest.fixture
def sample_scenario(db_session: Session, sample_scenario_data: ScenarioCreate):
    """Create a sample scenario for testing."""
    return create_scenario(db_session, sample_scenario_data)

@pytest.fixture
def sample_assumptions_data(sample_scenario: Scenario):
    """Create sample scenario assumptions data."""
    return ScenarioAssumptionCreate(
        scenario_id=sample_scenario.scenario_id,
        retirement_age_1=67,
        retirement_age_2=65,
        default_growth_rate=0.08,
        inflation_rate=0.035,
        annual_retirement_spending=75000.0
    )

def test_create_scenario(db_session: Session, sample_scenario_data: ScenarioCreate):
    """Test creating a scenario."""
    scenario = create_scenario(db_session, sample_scenario_data)
    
    assert scenario.plan_id == sample_scenario_data.plan_id
    assert scenario.scenario_name == "Test Scenario"
    assert scenario.scenario_color == "#FF0000"
    assert scenario.scenario_id is not None
    assert scenario.created_at is not None

def test_get_scenario(db_session: Session, sample_scenario: Scenario):
    """Test retrieving a scenario by ID."""
    retrieved_scenario = get_scenario(db_session, sample_scenario.scenario_id)
    
    assert retrieved_scenario is not None
    assert retrieved_scenario.scenario_id == sample_scenario.scenario_id
    assert retrieved_scenario.scenario_name == sample_scenario.scenario_name

def test_get_nonexistent_scenario(db_session: Session):
    """Test retrieving a non-existent scenario."""
    scenario = get_scenario(db_session, 999)
    assert scenario is None

def test_get_plan_scenarios(db_session: Session, sample_plan: Plan):
    """Test retrieving all scenarios for a plan."""
    # Create multiple scenarios
    scenario_data1 = ScenarioCreate(
        plan_id=sample_plan.plan_id,
        scenario_name="Scenario 1"
    )
    scenario_data2 = ScenarioCreate(
        plan_id=sample_plan.plan_id,
        scenario_name="Scenario 2"
    )
    
    create_scenario(db_session, scenario_data1)
    create_scenario(db_session, scenario_data2)
    
    scenarios = get_plan_scenarios(db_session, sample_plan.plan_id)
    assert len(scenarios) == 2
    assert all(s.plan_id == sample_plan.plan_id for s in scenarios)

def test_update_scenario(db_session: Session, sample_scenario: Scenario):
    """Test updating a scenario."""
    update_data = ScenarioUpdate(
        scenario_name="Updated Scenario",
        scenario_color="#00FF00"
    )
    
    updated_scenario = update_scenario(db_session, sample_scenario.scenario_id, update_data)
    assert updated_scenario is not None
    assert updated_scenario.scenario_name == "Updated Scenario"
    assert updated_scenario.scenario_color == "#00FF00"

def test_update_nonexistent_scenario(db_session: Session):
    """Test updating a non-existent scenario."""
    update_data = ScenarioUpdate(scenario_name="Updated")
    updated_scenario = update_scenario(db_session, 999, update_data)
    assert updated_scenario is None

def test_delete_scenario(db_session: Session, sample_scenario: Scenario):
    """Test deleting a scenario."""
    assert delete_scenario(db_session, sample_scenario.scenario_id) is True
    assert get_scenario(db_session, sample_scenario.scenario_id) is None

def test_delete_nonexistent_scenario(db_session: Session):
    """Test deleting a non-existent scenario."""
    assert delete_scenario(db_session, 999) is False

def test_create_scenario_assumptions(db_session: Session, sample_assumptions_data: ScenarioAssumptionCreate):
    """Test creating scenario assumptions."""
    assumptions = create_scenario_assumptions(db_session, sample_assumptions_data)
    
    assert assumptions.scenario_id == sample_assumptions_data.scenario_id
    assert assumptions.retirement_age_1 == 67
    assert assumptions.retirement_age_2 == 65
    assert assumptions.default_growth_rate == 0.08
    assert assumptions.inflation_rate == 0.035
    assert assumptions.annual_retirement_spending == 75000.0

def test_get_scenario_assumptions(db_session: Session, sample_assumptions_data: ScenarioAssumptionCreate):
    """Test retrieving scenario assumptions."""
    created_assumptions = create_scenario_assumptions(db_session, sample_assumptions_data)
    retrieved_assumptions = get_scenario_assumptions(db_session, created_assumptions.scenario_id)
    
    assert retrieved_assumptions is not None
    assert retrieved_assumptions.scenario_id == created_assumptions.scenario_id
    assert retrieved_assumptions.retirement_age_1 == created_assumptions.retirement_age_1

def test_update_scenario_assumptions(db_session: Session, sample_assumptions_data: ScenarioAssumptionCreate):
    """Test updating scenario assumptions."""
    assumptions = create_scenario_assumptions(db_session, sample_assumptions_data)
    
    update_data = ScenarioAssumptionUpdate(
        retirement_age_1=70,
        default_growth_rate=0.09,
        annual_retirement_spending=80000.0
    )
    
    updated_assumptions = update_scenario_assumptions(db_session, assumptions.scenario_id, update_data)
    assert updated_assumptions is not None
    assert updated_assumptions.retirement_age_1 == 70
    assert updated_assumptions.default_growth_rate == 0.09
    assert updated_assumptions.annual_retirement_spending == 80000.0
    # Other fields should remain unchanged
    assert updated_assumptions.retirement_age_2 == 65
    assert updated_assumptions.inflation_rate == 0.035 