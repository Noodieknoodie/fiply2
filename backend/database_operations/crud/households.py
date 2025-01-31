# backend/database_operations/crud/households.py

"""
Full CRUD operations following SQLAlchemy 2.0 style
Proper validation of DOBs as required by core logic
Handles both required Person 1 and optional Person 2 data
Maintains created_at and updated_at timestamps
Cascade deletion of related plans (through SQLAlchemy relationship)
Proper error handling and transaction management
Additional utility method for household summary including plan count
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import Household
from ..utils.time_validations import validate_dob

class HouseholdCRUD:
    """CRUD operations for household management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_household(
        self,
        household_name: str,
        person1_first_name: str,
        person1_last_name: str,
        person1_dob: date,
        person2_first_name: Optional[str] = None,
        person2_last_name: Optional[str] = None,
        person2_dob: Optional[date] = None
    ) -> Household:
        """
        Create a new household.
        
        Args:
            household_name: Name identifier for the household
            person1_first_name: First name of primary person
            person1_last_name: Last name of primary person
            person1_dob: Date of birth of primary person
            person2_first_name: Optional first name of secondary person
            person2_last_name: Optional last name of secondary person
            person2_dob: Optional date of birth of secondary person
            
        Returns:
            Newly created Household instance
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate required person1 DOB
        if not validate_dob(person1_dob):
            raise ValueError("Invalid date of birth for person 1")
            
        # Validate optional person2 DOB if provided
        if person2_dob and not validate_dob(person2_dob):
            raise ValueError("Invalid date of birth for person 2")
            
        # Create new household instance
        household = Household(
            household_name=household_name,
            person1_first_name=person1_first_name,
            person1_last_name=person1_last_name,
            person1_dob=person1_dob,
            person2_first_name=person2_first_name,
            person2_last_name=person2_last_name,
            person2_dob=person2_dob
        )
        
        try:
            self.session.add(household)
            self.session.commit()
            return household
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create household", orig=e)

    def get_household(self, household_id: int) -> Optional[Household]:
        """
        Retrieve a household by ID.
        
        Args:
            household_id: Primary key of household
            
        Returns:
            Household instance if found, None otherwise
        """
        stmt = select(Household).where(Household.household_id == household_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all_households(self) -> List[Household]:
        """
        Retrieve all households.
        
        Returns:
            List of all Household instances
        """
        stmt = select(Household)
        return list(self.session.execute(stmt).scalars().all())

    def update_household(
        self, 
        household_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Household]:
        """
        Update a household's information.
        
        Args:
            household_id: Primary key of household to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated Household instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate DOB if included in update
        if 'person1_dob' in update_data and not validate_dob(update_data['person1_dob']):
            raise ValueError("Invalid date of birth for person 1")
        if 'person2_dob' in update_data and update_data['person2_dob'] and not validate_dob(update_data['person2_dob']):
            raise ValueError("Invalid date of birth for person 2")

        try:
            # Update the timestamp
            update_data['updated_at'] = datetime.now()
            
            # Perform the update
            stmt = (
                update(Household)
                .where(Household.household_id == household_id)
                .values(**update_data)
                .returning(Household)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update household", orig=e)

    def delete_household(self, household_id: int) -> bool:
        """
        Delete a household.
        
        Args:
            household_id: Primary key of household to delete
            
        Returns:
            True if household was deleted, False if not found
        """
        stmt = delete(Household).where(Household.household_id == household_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_household_summary(self, household_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of household information including plan count.
        
        Args:
            household_id: Primary key of household
            
        Returns:
            Dictionary containing household summary if found, None otherwise
        """
        household = self.get_household(household_id)
        if not household:
            return None
            
        return {
            'household_id': household.household_id,
            'household_name': household.household_name,
            'person1_name': f"{household.person1_first_name} {household.person1_last_name}",
            'person2_name': f"{household.person2_first_name} {household.person2_last_name}" if household.person2_first_name else None,
            'plan_count': len(household.plans),
            'created_at': household.created_at,
            'updated_at': household.updated_at
        }