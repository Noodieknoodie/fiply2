from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from database_operations.models import Plan, Household, LiabilityCategory, Liability, Base
from database_operations.connection import get_session
from database_operations.crud.financial.liabilities import (
    LiabilityCategoryCreate,
    LiabilityCategoryUpdate,
    LiabilityCreate,
    LiabilityUpdate,
    create_liability_category,
    get_liability_category,
    get_plan_liability_categories,
    update_liability_category,
    delete_liability_category,
    reorder_liability_categories,
    create_liability,
    get_liability,
    get_category_liabilities,
    get_plan_liabilities,
    update_liability,
    delete_liability
)
from database_operations.crud.plans import PlanCreate, create_plan
from database_operations.crud.households import HouseholdCreate, create_household

@pytest.fixture(autouse=True)
def cleanup_database():
    """Cleanup the database before each test."""
    session = get_session()
    try:
        Base.metadata.drop_all(bind=session.get_bind())
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
def sample_category_data(sample_plan: Plan):
    """Create sample category data."""
    return LiabilityCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Test Category"
    )

@pytest.fixture
def sample_category(db_session: Session, sample_category_data: LiabilityCategoryCreate):
    """Create a sample liability category for testing."""
    return create_liability_category(db_session, sample_category_data)

@pytest.fixture
def sample_liability_data(sample_plan: Plan, sample_category: LiabilityCategory):
    """Create sample liability data."""
    return LiabilityCreate(
        plan_id=sample_plan.plan_id,
        liability_category_id=sample_category.liability_category_id,
        liability_name="Test Liability",
        owner="Person 1",
        value=250000.0,
        interest_rate=0.035
    )

def test_create_liability_category(db_session: Session, sample_category_data: LiabilityCategoryCreate):
    """Test creating a liability category."""
    category = create_liability_category(db_session, sample_category_data)
    assert category.plan_id == sample_category_data.plan_id
    assert category.category_name == "Test Category"
    assert category.category_order == 1  # First category should be order 1

def test_get_liability_category(db_session: Session, sample_category: LiabilityCategory):
    """Test retrieving a liability category by ID."""
    retrieved_category = get_liability_category(db_session, sample_category.liability_category_id)
    assert retrieved_category is not None
    assert retrieved_category.liability_category_id == sample_category.liability_category_id
    assert retrieved_category.category_name == sample_category.category_name

def test_get_nonexistent_category(db_session: Session):
    """Test retrieving a non-existent category."""
    category = get_liability_category(db_session, 999)
    assert category is None

def test_get_plan_liability_categories(db_session: Session, sample_plan: Plan):
    """Test retrieving all categories for a plan."""
    category_data1 = LiabilityCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 1"
    )
    category_data2 = LiabilityCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 2"
    )
    
    create_liability_category(db_session, category_data1)
    create_liability_category(db_session, category_data2)
    
    categories = get_plan_liability_categories(db_session, sample_plan.plan_id)
    assert len(categories) == 2
    assert all(c.plan_id == sample_plan.plan_id for c in categories)
    assert categories[0].category_order < categories[1].category_order

def test_update_liability_category(db_session: Session, sample_category: LiabilityCategory):
    """Test updating a liability category."""
    update_data = LiabilityCategoryUpdate(
        category_name="Updated Category",
        category_order=5
    )
    
    updated_category = update_liability_category(db_session, sample_category.liability_category_id, update_data)
    assert updated_category is not None
    assert updated_category.category_name == "Updated Category"
    assert updated_category.category_order == 5

def test_delete_liability_category(db_session: Session, sample_category: LiabilityCategory):
    """Test deleting a liability category."""
    assert delete_liability_category(db_session, sample_category.liability_category_id) is True
    assert get_liability_category(db_session, sample_category.liability_category_id) is None

def test_reorder_liability_categories(db_session: Session, sample_plan: Plan):
    """Test reordering liability categories."""
    cat1 = create_liability_category(db_session, LiabilityCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 1"
    ))
    cat2 = create_liability_category(db_session, LiabilityCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 2"
    ))
    
    new_orders = {
        cat1.liability_category_id: 2,
        cat2.liability_category_id: 1
    }
    
    updated_categories = reorder_liability_categories(db_session, sample_plan.plan_id, new_orders)
    assert len(updated_categories) == 2
    assert updated_categories[0].liability_category_id == cat2.liability_category_id
    assert updated_categories[1].liability_category_id == cat1.liability_category_id

def test_create_liability(db_session: Session, sample_liability_data: LiabilityCreate):
    """Test creating a liability."""
    liability = create_liability(db_session, sample_liability_data)
    assert liability.plan_id == sample_liability_data.plan_id
    assert liability.liability_category_id == sample_liability_data.liability_category_id
    assert liability.liability_name == "Test Liability"
    assert liability.owner == "Person 1"
    assert liability.value == 250000.0
    assert liability.interest_rate == 0.035
    assert liability.include_in_nest_egg == True

def test_get_liability(db_session: Session, sample_liability_data: LiabilityCreate):
    """Test retrieving a liability by ID."""
    created_liability = create_liability(db_session, sample_liability_data)
    retrieved_liability = get_liability(db_session, created_liability.liability_id)
    assert retrieved_liability is not None
    assert retrieved_liability.liability_id == created_liability.liability_id
    assert retrieved_liability.liability_name == created_liability.liability_name

def test_get_category_liabilities(db_session: Session, sample_category: LiabilityCategory, sample_liability_data: LiabilityCreate):
    """Test retrieving all liabilities in a category."""
    liability_data1 = LiabilityCreate(
        plan_id=sample_liability_data.plan_id,
        liability_category_id=sample_category.liability_category_id,
        liability_name="Liability 1",
        owner="Person 1",
        value=150000.0,
        interest_rate=0.04
    )
    liability_data2 = LiabilityCreate(
        plan_id=sample_liability_data.plan_id,
        liability_category_id=sample_category.liability_category_id,
        liability_name="Liability 2",
        owner="Person 2",
        value=75000.0,
        interest_rate=0.035
    )
    
    create_liability(db_session, liability_data1)
    create_liability(db_session, liability_data2)
    
    liabilities = get_category_liabilities(db_session, sample_category.liability_category_id)
    assert len(liabilities) == 2
    assert all(l.liability_category_id == sample_category.liability_category_id for l in liabilities)

def test_get_plan_liabilities(db_session: Session, sample_plan: Plan, sample_category: LiabilityCategory, sample_liability_data: LiabilityCreate):
    """Test retrieving all liabilities for a plan."""
    liability_data1 = LiabilityCreate(
        plan_id=sample_plan.plan_id,
        liability_category_id=sample_category.liability_category_id,
        liability_name="Liability 1",
        owner="Person 1",
        value=150000.0,
        interest_rate=0.04
    )
    liability_data2 = LiabilityCreate(
        plan_id=sample_plan.plan_id,
        liability_category_id=sample_category.liability_category_id,
        liability_name="Liability 2",
        owner="Person 2",
        value=75000.0,
        interest_rate=0.035
    )
    
    create_liability(db_session, liability_data1)
    create_liability(db_session, liability_data2)
    
    liabilities = get_plan_liabilities(db_session, sample_plan.plan_id)
    assert len(liabilities) == 2
    assert all(l.plan_id == sample_plan.plan_id for l in liabilities)
    
    # Test with categories
    liabilities = get_plan_liabilities(db_session, sample_plan.plan_id, include_categories=True)
    assert len(liabilities) == 2
    assert all(l.category.liability_category_id == sample_category.liability_category_id for l in liabilities)

def test_update_liability(db_session: Session, sample_liability_data: LiabilityCreate):
    """Test updating a liability."""
    liability = create_liability(db_session, sample_liability_data)
    
    update_data = LiabilityUpdate(
        liability_name="Updated Liability",
        value=300000.0,
        interest_rate=0.045,
        include_in_nest_egg=False
    )
    
    updated_liability = update_liability(db_session, liability.liability_id, update_data)
    assert updated_liability is not None
    assert updated_liability.liability_name == "Updated Liability"
    assert updated_liability.value == 300000.0
    assert updated_liability.interest_rate == 0.045
    assert updated_liability.include_in_nest_egg == False
    assert updated_liability.owner == "Person 1"  # Unchanged field

def test_delete_liability(db_session: Session, sample_liability_data: LiabilityCreate):
    """Test deleting a liability."""
    liability = create_liability(db_session, sample_liability_data)
    assert delete_liability(db_session, liability.liability_id) is True
    assert get_liability(db_session, liability.liability_id) is None 