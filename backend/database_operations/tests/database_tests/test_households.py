from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from database_operations.models import Base, Household
from database_operations.connection import get_session
from database_operations.crud.households import (
    HouseholdCreate,
    HouseholdUpdate,
    create_household,
    get_household,
    get_households,
    update_household,
    delete_household
)

@pytest.fixture(autouse=True)
def cleanup_database():
    """Cleanup the database before each test."""
    session = get_session()
    try:
        # Delete all households
        session.execute(delete(Household))
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
def sample_household():
    """Fixture that provides sample household data."""
    return HouseholdCreate(
        household_name="Test Family",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1980, 1, 1),
        person2_first_name="Jane",
        person2_last_name="Doe",
        person2_dob=date(1982, 2, 2)
    )

def test_create_household(db_session: Session, sample_household: HouseholdCreate):
    """Test creating a household."""
    household = create_household(db_session, sample_household)
    
    assert household.household_name == "Test Family"
    assert household.person1_first_name == "John"
    assert household.person1_last_name == "Doe"
    assert household.person1_dob == date(1980, 1, 1)
    assert household.person2_first_name == "Jane"
    assert household.person2_last_name == "Doe"
    assert household.person2_dob == date(1982, 2, 2)
    assert household.household_id is not None

def test_create_household_without_person2(db_session: Session):
    """Test creating a household with only one person."""
    household_data = HouseholdCreate(
        household_name="Single Person Family",
        person1_first_name="John",
        person1_last_name="Smith",
        person1_dob=date(1975, 6, 15)
    )
    
    household = create_household(db_session, household_data)
    
    assert household.household_name == "Single Person Family"
    assert household.person1_first_name == "John"
    assert household.person2_first_name is None
    assert household.person2_last_name is None
    assert household.person2_dob is None

def test_get_household(db_session: Session, sample_household: HouseholdCreate):
    """Test retrieving a household by ID."""
    created = create_household(db_session, sample_household)
    retrieved = get_household(db_session, created.household_id)
    
    assert retrieved is not None
    assert retrieved.household_id == created.household_id
    assert retrieved.household_name == created.household_name

def test_get_nonexistent_household(db_session: Session):
    """Test retrieving a non-existent household."""
    household = get_household(db_session, 999999)
    assert household is None

def test_get_households(db_session: Session, sample_household: HouseholdCreate):
    """Test retrieving multiple households with pagination."""
    # Create multiple households
    create_household(db_session, sample_household)
    create_household(
        db_session,
        HouseholdCreate(
            household_name="Another Family",
            person1_first_name="Bob",
            person1_last_name="Wilson",
            person1_dob=date(1990, 3, 3)
        )
    )
    
    # Test pagination
    households = get_households(db_session, skip=0, limit=1)
    assert len(households) == 1
    
    # Test search
    searched = get_households(db_session, search="Another")
    assert len(searched) == 1
    assert searched[0].household_name == "Another Family"
    
    # Test getting all
    all_households = get_households(db_session)
    assert len(all_households) == 2

def test_update_household(db_session: Session, sample_household: HouseholdCreate):
    """Test updating a household."""
    created = create_household(db_session, sample_household)
    
    update_data = HouseholdUpdate(
        household_name="Updated Family Name",
        person2_first_name="Janet"
    )
    
    updated = update_household(db_session, created.household_id, update_data)
    
    assert updated is not None
    assert updated.household_name == "Updated Family Name"
    assert updated.person2_first_name == "Janet"
    # Unchanged fields should remain the same
    assert updated.person1_first_name == "John"

def test_update_nonexistent_household(db_session: Session):
    """Test updating a non-existent household."""
    update_data = HouseholdUpdate(household_name="New Name")
    updated = update_household(db_session, 999999, update_data)
    assert updated is None

def test_delete_household(db_session: Session, sample_household: HouseholdCreate):
    """Test deleting a household."""
    created = create_household(db_session, sample_household)
    
    # Verify deletion
    success = delete_household(db_session, created.household_id)
    assert success is True
    
    # Verify it's gone
    deleted = get_household(db_session, created.household_id)
    assert deleted is None

def test_delete_nonexistent_household(db_session: Session):
    """Test deleting a non-existent household."""
    success = delete_household(db_session, 999999)
    assert success is False 