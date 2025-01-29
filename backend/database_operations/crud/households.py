from datetime import date
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Household

class HouseholdCreate:
    """Schema for creating a household."""
    def __init__(
        self,
        household_name: str,
        person1_first_name: str,
        person1_last_name: str,
        person1_dob: date,
        person2_first_name: Optional[str] = None,
        person2_last_name: Optional[str] = None,
        person2_dob: Optional[date] = None,
    ):
        self.household_name = household_name
        self.person1_first_name = person1_first_name
        self.person1_last_name = person1_last_name
        self.person1_dob = person1_dob
        self.person2_first_name = person2_first_name
        self.person2_last_name = person2_last_name
        self.person2_dob = person2_dob

class HouseholdUpdate:
    """Schema for updating a household."""
    def __init__(
        self,
        household_name: Optional[str] = None,
        person1_first_name: Optional[str] = None,
        person1_last_name: Optional[str] = None,
        person1_dob: Optional[date] = None,
        person2_first_name: Optional[str] = None,
        person2_last_name: Optional[str] = None,
        person2_dob: Optional[date] = None,
    ):
        self.household_name = household_name
        self.person1_first_name = person1_first_name
        self.person1_last_name = person1_last_name
        self.person1_dob = person1_dob
        self.person2_first_name = person2_first_name
        self.person2_last_name = person2_last_name
        self.person2_dob = person2_dob

def create_household(db: Session, household: HouseholdCreate) -> Household:
    """Create a new household."""
    db_household = Household(
        household_name=household.household_name,
        person1_first_name=household.person1_first_name,
        person1_last_name=household.person1_last_name,
        person1_dob=household.person1_dob,
        person2_first_name=household.person2_first_name,
        person2_last_name=household.person2_last_name,
        person2_dob=household.person2_dob,
    )
    db.add(db_household)
    db.commit()
    db.refresh(db_household)
    return db_household

def get_household(db: Session, household_id: int) -> Optional[Household]:
    """Get a household by ID."""
    stmt = select(Household).where(Household.household_id == household_id)
    return db.scalar(stmt)

def get_households(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Household]:
    """Get all households with optional pagination and search."""
    stmt = select(Household)
    
    if search:
        search_filter = (
            Household.household_name.ilike(f"%{search}%") |
            Household.person1_first_name.ilike(f"%{search}%") |
            Household.person1_last_name.ilike(f"%{search}%") |
            Household.person2_first_name.ilike(f"%{search}%") |
            Household.person2_last_name.ilike(f"%{search}%")
        )
        stmt = stmt.where(search_filter)
    
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))

def update_household(
    db: Session,
    household_id: int,
    household_update: HouseholdUpdate
) -> Optional[Household]:
    """Update a household."""
    stmt = select(Household).where(Household.household_id == household_id)
    db_household = db.scalar(stmt)
    
    if not db_household:
        return None
    
    # Update only provided fields
    update_data = household_update.__dict__
    for field, value in update_data.items():
        if value is not None:
            setattr(db_household, field, value)
    
    db.commit()
    db.refresh(db_household)
    return db_household

def delete_household(db: Session, household_id: int) -> bool:
    """Delete a household."""
    stmt = select(Household).where(Household.household_id == household_id)
    db_household = db.scalar(stmt)
    
    if not db_household:
        return False
    
    db.delete(db_household)
    db.commit()
    return True 