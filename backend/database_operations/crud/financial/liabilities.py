# backend/database_operations/crud/financial/liabilities.py
"""
Full CRUD operations for liabilities following SQLAlchemy 2.0 style
Simple interest rate handling (vs. complex growth rates for assets)
Proper validation of:
Liability values (positive)
Interest rates (if provided)
Owner values
Support for filtering liabilities by category
Comprehensive liability summary
Additional utility for calculating total liabilities
Proper error handling and transaction management
Support for nest egg inclusion/exclusion
The key difference from assets.py is the simpler growth model - liabilities just have an optional interest rate rather than the complex growth rate configurations used for assets.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import Liability, LiabilityCategory, Plan
from ...utils.money_validations import validate_positive_amount, validate_rate

class LiabilityCRUD:
    """CRUD operations for liability management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_liability(
        self,
        plan_id: int,
        liability_category_id: int,
        liability_name: str,
        value: float,
        owner: str,
        interest_rate: Optional[float] = None,
        include_in_nest_egg: bool = True
    ) -> Liability:
        """
        Create a new liability.
        
        Args:
            plan_id: ID of plan this liability belongs to
            liability_category_id: ID of liability category
            liability_name: Name identifier for the liability
            value: Current value of the liability
            owner: Owner of the liability ('person1', 'person2', or 'joint')
            interest_rate: Optional annual interest rate
            include_in_nest_egg: Whether to include in retirement calculations
            
        Returns:
            Newly created Liability instance
            
        Raises:
            ValueError: If validation fails
            NoResultFound: If plan_id or category_id don't exist
            IntegrityError: If database constraint violated
        """
        # Verify plan and category exist
        stmt = select(Plan).join(LiabilityCategory).where(
            and_(
                Plan.plan_id == plan_id,
                LiabilityCategory.liability_category_id == liability_category_id
            )
        )
        if not self.session.execute(stmt).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} or category {liability_category_id} not found")

        # Validate input
        validate_positive_amount(value, "liability_value")
        if interest_rate is not None:
            validate_rate(interest_rate, "interest_rate")
        if owner not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        # Create liability instance
        liability = Liability(
            plan_id=plan_id,
            liability_category_id=liability_category_id,
            liability_name=liability_name,
            value=value,
            owner=owner,
            interest_rate=interest_rate,
            include_in_nest_egg=include_in_nest_egg
        )
        
        try:
            self.session.add(liability)
            self.session.commit()
            return liability
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create liability", orig=e)

    def get_liability(self, liability_id: int) -> Optional[Liability]:
        """
        Retrieve a liability by ID.
        
        Args:
            liability_id: Primary key of liability
            
        Returns:
            Liability instance if found, None otherwise
        """
        stmt = select(Liability).where(Liability.liability_id == liability_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_liabilities(
        self, 
        plan_id: int,
        category_id: Optional[int] = None
    ) -> List[Liability]:
        """
        Retrieve all liabilities for a plan, optionally filtered by category.
        
        Args:
            plan_id: ID of plan to get liabilities for
            category_id: Optional category ID to filter by
            
        Returns:
            List of Liability instances
        """
        stmt = select(Liability).where(Liability.plan_id == plan_id)
        
        if category_id:
            stmt = stmt.where(Liability.liability_category_id == category_id)
            
        return list(self.session.execute(stmt).scalars().all())

    def update_liability(
        self,
        liability_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Liability]:
        """
        Update a liability.
        
        Args:
            liability_id: Primary key of liability to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated Liability instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate value if included in update
        if 'value' in update_data:
            validate_positive_amount(update_data['value'], "liability_value")

        # Validate interest rate if included in update
        if 'interest_rate' in update_data and update_data['interest_rate'] is not None:
            validate_rate(update_data['interest_rate'], "interest_rate")

        # Validate owner if included in update
        if 'owner' in update_data and update_data['owner'] not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        try:
            stmt = (
                update(Liability)
                .where(Liability.liability_id == liability_id)
                .values(**update_data)
                .returning(Liability)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update liability", orig=e)

    def delete_liability(self, liability_id: int) -> bool:
        """
        Delete a liability.
        
        Args:
            liability_id: Primary key of liability to delete
            
        Returns:
            True if liability was deleted, False if not found
        """
        stmt = delete(Liability).where(Liability.liability_id == liability_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_liability_summary(self, liability_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of liability information.
        
        Args:
            liability_id: Primary key of liability
            
        Returns:
            Dictionary containing liability summary if found, None otherwise
        """
        liability = self.get_liability(liability_id)
        if not liability:
            return None
            
        return {
            'liability_id': liability.liability_id,
            'liability_name': liability.liability_name,
            'category_id': liability.liability_category_id,
            'value': liability.value,
            'owner': liability.owner,
            'interest_rate': liability.interest_rate,
            'include_in_nest_egg': liability.include_in_nest_egg,
            'has_interest': liability.interest_rate is not None
        }

    def get_total_liabilities(
        self,
        plan_id: int,
        include_in_nest_egg_only: bool = False
    ) -> float:
        """
        Calculate total liability value for a plan.
        
        Args:
            plan_id: ID of plan to calculate total for
            include_in_nest_egg_only: If True, only sum liabilities marked for nest egg
            
        Returns:
            Total value of all matching liabilities
        """
        stmt = select(Liability).where(Liability.plan_id == plan_id)
        
        if include_in_nest_egg_only:
            stmt = stmt.where(Liability.include_in_nest_egg == True)
            
        liabilities = self.session.execute(stmt).scalars().all()
        return sum(liability.value for liability in liabilities)