"""Tests for cash flows CRUD operations."""

from datetime import date
import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..models import Base, Household, Plan, InflowOutflow
from ..crud.financial.cash_flows import (
    InflowOutflowCreate,
    InflowOutflowUpdate,
    create_inflow_outflow,
    get_inflow_outflow,
    get_plan_cash_flows,
    update_inflow_outflow,
    delete_inflow_outflow
)

@pytest.fixture(autouse=True)
def cleanup_database(db_session: Session):
    """Cleanup the database before each test."""
    try:
        db_session.execute(delete(InflowOutflow))
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
def sample_cash_flow_data(sample_plan: Plan) -> InflowOutflowCreate:
    """Create sample cash flow data."""
    return InflowOutflowCreate(
        plan_id=sample_plan.plan_id,
        type="inflow",
        name="Salary",
        annual_amount=100000.0,
        start_date=date(2024, 1, 1),
        end_date=date(2054, 12, 31),
        apply_inflation=True
    )

def test_create_inflow_outflow(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test creating an inflow/outflow."""
    try:
        cash_flow = create_inflow_outflow(db_session, sample_cash_flow_data)
        assert cash_flow is not None
        assert cash_flow.plan_id == sample_cash_flow_data.plan_id
        assert cash_flow.type == "inflow"
        assert cash_flow.name == "Salary"
        assert cash_flow.annual_amount == 100000.0
        assert cash_flow.start_date == date(2024, 1, 1)
        assert cash_flow.end_date == date(2054, 12, 31)
        # SQLite stores booleans as integers
        assert cash_flow.apply_inflation == 1
    finally:
        db_session.rollback()

def test_create_inflow_outflow_invalid_plan(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test creating an inflow/outflow with invalid plan ID."""
    try:
        invalid_data = InflowOutflowCreate(**vars(sample_cash_flow_data))
        invalid_data.plan_id = 999
        cash_flow = create_inflow_outflow(db_session, invalid_data)
        assert cash_flow is None
    finally:
        db_session.rollback()

def test_get_inflow_outflow(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test retrieving an inflow/outflow."""
    try:
        created = create_inflow_outflow(db_session, sample_cash_flow_data)
        assert created is not None
        
        retrieved = get_inflow_outflow(db_session, created.inflow_outflow_id)
        assert retrieved is not None
        assert retrieved.name == "Salary"
        assert retrieved.annual_amount == 100000.0
        # Verify plan relationship is loaded
        assert retrieved.plan is not None
        assert retrieved.plan.plan_id == sample_cash_flow_data.plan_id
    finally:
        db_session.rollback()

def test_get_nonexistent_inflow_outflow(db_session: Session):
    """Test retrieving a non-existent inflow/outflow."""
    try:
        retrieved = get_inflow_outflow(db_session, 999)
        assert retrieved is None
    finally:
        db_session.rollback()

def test_get_plan_cash_flows(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test retrieving all cash flows for a plan."""
    try:
        # Create an inflow
        created_inflow = create_inflow_outflow(db_session, sample_cash_flow_data)
        assert created_inflow is not None
        
        # Create an outflow
        outflow_data = InflowOutflowCreate(
            plan_id=sample_cash_flow_data.plan_id,
            type="outflow",
            name="Rent",
            annual_amount=24000.0,
            start_date=date(2024, 1, 1)
        )
        created_outflow = create_inflow_outflow(db_session, outflow_data)
        assert created_outflow is not None
        
        # Test getting all cash flows
        all_flows = get_plan_cash_flows(db_session, sample_cash_flow_data.plan_id)
        assert len(all_flows) == 2
        
        # Test filtering by type
        inflows = get_plan_cash_flows(db_session, sample_cash_flow_data.plan_id, flow_type="inflow")
        assert len(inflows) == 1
        assert inflows[0].name == "Salary"
        
        outflows = get_plan_cash_flows(db_session, sample_cash_flow_data.plan_id, flow_type="outflow")
        assert len(outflows) == 1
        assert outflows[0].name == "Rent"
    finally:
        db_session.rollback()

def test_update_inflow_outflow(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test updating an inflow/outflow."""
    try:
        cash_flow = create_inflow_outflow(db_session, sample_cash_flow_data)
        assert cash_flow is not None
        
        update_data = InflowOutflowUpdate(
            name="Updated Salary",
            annual_amount=110000.0,
            apply_inflation=False
        )
        
        updated = update_inflow_outflow(db_session, cash_flow.inflow_outflow_id, update_data)
        assert updated is not None
        assert updated.name == "Updated Salary"
        assert updated.annual_amount == 110000.0
        # SQLite stores booleans as integers
        assert updated.apply_inflation == 0
        # Unchanged fields should remain the same
        assert updated.start_date == date(2024, 1, 1)
        assert updated.end_date == date(2054, 12, 31)
    finally:
        db_session.rollback()

def test_update_nonexistent_inflow_outflow(db_session: Session):
    """Test updating a non-existent inflow/outflow."""
    try:
        update_data = InflowOutflowUpdate(name="Updated Name")
        updated = update_inflow_outflow(db_session, 999, update_data)
        assert updated is None
    finally:
        db_session.rollback()

def test_delete_inflow_outflow(db_session: Session, sample_cash_flow_data: InflowOutflowCreate):
    """Test deleting an inflow/outflow."""
    try:
        cash_flow = create_inflow_outflow(db_session, sample_cash_flow_data)
        assert cash_flow is not None
        
        assert delete_inflow_outflow(db_session, cash_flow.inflow_outflow_id) == True
        assert get_inflow_outflow(db_session, cash_flow.inflow_outflow_id) is None
    finally:
        db_session.rollback()

def test_delete_nonexistent_inflow_outflow(db_session: Session):
    """Test deleting a non-existent inflow/outflow."""
    try:
        assert delete_inflow_outflow(db_session, 999) == False
    finally:
        db_session.rollback() 