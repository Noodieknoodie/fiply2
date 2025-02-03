# backend/database_operations/crud/base_assumptions.py
"""
Full CRUD operations for base assumptions following SQLAlchemy 2.0 style
Comprehensive validation:
Retirement and final ages within bounds
Valid age sequences for both people
Growth and inflation rates
Final age selector logic
Dynamic year calculations based on DOB and ages
Proper error handling and transaction management
Support for optional person 2 data
Validation against household data through plan relationship
Utility method for getting absolute year mappings
"""

from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import BaseAssumption, Plan
from ..validation.time_validation import (
    validate_retirement_age,
    validate_final_age,
    validate_age_sequence
)
from ..validation.money_validation import validate_rate



class BaseAssumptionCRUD:
    """CRUD operations for plan base assumptions."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_base_assumptions(
        self,
        plan_id: int,
        retirement_age_1: int,
        final_age_1: int,
        default_growth_rate: float,
        inflation_rate: float,
        retirement_age_2: Optional[int] = None,
        final_age_2: Optional[int] = None,
        final_age_selector: int = 1,
    ) -> BaseAssumption:
        """
        Create base assumptions for a plan.
        
        Args:
            plan_id: ID of plan these assumptions belong to
            retirement_age_1: Retirement age for person 1
            final_age_1: Final age (life expectancy) for person 1
            default_growth_rate: Default annual growth rate for assets
            inflation_rate: Annual inflation rate
            retirement_age_2: Optional retirement age for person 2
            final_age_2: Optional final age for person 2
            final_age_selector: Which person's final age to use (1 or 2)
            
        Returns:
            Newly created BaseAssumption instance
            
        Raises:
            ValueError: If validation fails
            NoResultFound: If plan_id doesn't exist
            IntegrityError: If database constraint violated
        """
        # Verify plan exists
        stmt = select(Plan).where(Plan.plan_id == plan_id)
        plan = self.session.execute(stmt).scalar_one_or_none()
        if not plan:
            raise NoResultFound(f"Plan {plan_id} not found")

        # Validate retirement and final ages for person 1
        if not validate_retirement_age(retirement_age_1):
            raise ValueError("Invalid retirement age for person 1")
        if not validate_final_age(final_age_1):
            raise ValueError("Invalid final age for person 1")
        if not validate_age_sequence(plan.household.person1_dob.year, retirement_age_1, final_age_1):
            raise ValueError("Invalid age sequence for person 1")

        # Validate person 2 ages if provided
        if retirement_age_2 is not None:
            if not validate_retirement_age(retirement_age_2):
                raise ValueError("Invalid retirement age for person 2")
            if final_age_2 is not None:
                if not validate_final_age(final_age_2):
                    raise ValueError("Invalid final age for person 2")
                if not validate_age_sequence(plan.household.person2_dob.year, retirement_age_2, final_age_2):
                    raise ValueError("Invalid age sequence for person 2")

        # Validate rates
        validate_rate(default_growth_rate, "default_growth_rate")
        validate_rate(inflation_rate, "inflation_rate")

        # Validate final age selector
        if final_age_selector not in [1, 2]:
            raise ValueError("final_age_selector must be 1 or 2")
        if final_age_selector == 2 and final_age_2 is None:
            raise ValueError("Cannot select person 2's final age when it's not provided")

        # Create base assumptions instance
        base_assumptions = BaseAssumption(
            plan_id=plan_id,
            retirement_age_1=retirement_age_1,
            retirement_age_2=retirement_age_2,
            final_age_1=final_age_1,
            final_age_2=final_age_2,
            final_age_selector=final_age_selector,
            default_growth_rate=default_growth_rate,
            inflation_rate=inflation_rate
        )
        
        try:
            self.session.add(base_assumptions)
            self.session.commit()
            return base_assumptions
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create base assumptions", orig=e)

    def get_base_assumptions(self, plan_id: int) -> Optional[BaseAssumption]:
        """
        Retrieve base assumptions for a plan.
        
        Args:
            plan_id: ID of plan to get assumptions for
            
        Returns:
            BaseAssumption instance if found, None otherwise
        """
        stmt = select(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def update_base_assumptions(
        self,
        plan_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[BaseAssumption]:
        """
        Update base assumptions.
        
        Args:
            plan_id: ID of plan whose assumptions to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated BaseAssumption instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Get current assumptions and plan for validation
        stmt = select(BaseAssumption, Plan).join(Plan).where(BaseAssumption.plan_id == plan_id)
        result = self.session.execute(stmt).first()
        if not result:
            return None
        
        current_assumptions, plan = result

        # Validate rates if provided
        if 'default_growth_rate' in update_data:
            validate_rate(update_data['default_growth_rate'], "default_growth_rate")
        if 'inflation_rate' in update_data:
            validate_rate(update_data['inflation_rate'], "inflation_rate")

        # Validate ages if provided
        retirement_age_1 = update_data.get('retirement_age_1', current_assumptions.retirement_age_1)
        final_age_1 = update_data.get('final_age_1', current_assumptions.final_age_1)
        retirement_age_2 = update_data.get('retirement_age_2', current_assumptions.retirement_age_2)
        final_age_2 = update_data.get('final_age_2', current_assumptions.final_age_2)

        if 'retirement_age_1' in update_data or 'final_age_1' in update_data:
            if not validate_age_sequence(plan.household.person1_dob.year, retirement_age_1, final_age_1):
                raise ValueError("Invalid age sequence for person 1")

        if (retirement_age_2 is not None and 
            ('retirement_age_2' in update_data or 'final_age_2' in update_data)):
            if not validate_age_sequence(plan.household.person2_dob.year, retirement_age_2, final_age_2):
                raise ValueError("Invalid age sequence for person 2")

        try:
            # Perform the update
            stmt = (
                update(BaseAssumption)
                .where(BaseAssumption.plan_id == plan_id)
                .values(**update_data)
                .returning(BaseAssumption)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update base assumptions", orig=e)

    def delete_base_assumptions(self, plan_id: int) -> bool:
        """
        Delete base assumptions for a plan.
        
        Args:
            plan_id: ID of plan whose assumptions to delete
            
        Returns:
            True if assumptions were deleted, False if not found
        """
        stmt = delete(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_year_mappings(self, plan_id: int) -> Dict[str, int]:
        """
        Get absolute year mappings for key plan dates.
        
        Args:
            plan_id: ID of plan to get mappings for
            
        Returns:
            Dictionary containing start_year, retirement_year, and end_year
            
        Raises:
            NoResultFound: If plan or assumptions not found
        """
        # Get plan and assumptions with household data
        stmt = (
            select(BaseAssumption, Plan)
            .join(Plan)
            .where(BaseAssumption.plan_id == plan_id)
        )
        result = self.session.execute(stmt).first()
        if not result:
            raise NoResultFound(f"Base assumptions not found for plan {plan_id}")
            
        assumptions, plan = result
        
        # Determine which DOB to use based on final_age_selector
        if assumptions.final_age_selector == 1:
            dob = plan.household.person1_dob
            retirement_age = assumptions.retirement_age_1
            final_age = assumptions.final_age_1
        else:
            dob = plan.household.person2_dob
            retirement_age = assumptions.retirement_age_2
            final_age = assumptions.final_age_2

        # Calculate years
        start_year = datetime.now().year  # Always starts in current year
        retirement_year = dob.year + retirement_age
        end_year = dob.year + final_age

        return {
            'start_year': start_year,
            'retirement_year': retirement_year,
            'end_year': end_year
        }