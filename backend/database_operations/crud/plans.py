# backend/database_operations/crud/plans.py

"""
Full CRUD operations for plans following SQLAlchemy 2.0 style
Optional eager loading of relationships for detailed queries
Household existence verification on plan creation
Comprehensive plan summary including related entity counts
Timeline validation based on core logic requirements
Proper error handling and transaction management
Maintains created_at and updated_at timestamps
Cascade deletion handled through SQLAlchemy relationships
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import Plan, Household, BaseAssumption
from ..utils.time_validations import validate_projection_timeline

class PlanCRUD:
    """CRUD operations for financial plan management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_plan(
        self,
        household_id: int,
        plan_name: str,
    ) -> Plan:
        """
        Create a new financial plan for a household.
        
        Args:
            household_id: ID of household this plan belongs to
            plan_name: Name identifier for the plan
            
        Returns:
            Newly created Plan instance
            
        Raises:
            NoResultFound: If household_id doesn't exist
            IntegrityError: If database constraint violated
        """
        # Verify household exists
        stmt = select(Household).where(Household.household_id == household_id)
        if not self.session.execute(stmt).scalar_one_or_none():
            raise NoResultFound(f"Household {household_id} not found")
            
        # Create new plan instance
        plan = Plan(
            household_id=household_id,
            plan_name=plan_name,
        )
        
        try:
            self.session.add(plan)
            self.session.commit()
            return plan
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create plan", orig=e)

    def get_plan(self, plan_id: int, include_relationships: bool = False) -> Optional[Plan]:
        """
        Retrieve a plan by ID.
        
        Args:
            plan_id: Primary key of plan
            include_relationships: If True, eagerly loads all related data
            
        Returns:
            Plan instance if found, None otherwise
        """
        stmt = select(Plan).where(Plan.plan_id == plan_id)
        
        if include_relationships:
            stmt = stmt.options(
                joinedload(Plan.base_assumptions),
                joinedload(Plan.scenarios),
                joinedload(Plan.asset_categories),
                joinedload(Plan.liability_categories),
                joinedload(Plan.assets),
                joinedload(Plan.liabilities),
                joinedload(Plan.inflows_outflows),
                joinedload(Plan.retirement_income_plans)
            )
            
        return self.session.execute(stmt).scalar_one_or_none()

    def get_household_plans(self, household_id: int) -> List[Plan]:
        """
        Retrieve all plans for a specific household.
        
        Args:
            household_id: ID of household to get plans for
            
        Returns:
            List of Plan instances
        """
        stmt = select(Plan).where(Plan.household_id == household_id)
        return list(self.session.execute(stmt).scalars().all())

    def update_plan(
        self,
        plan_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Plan]:
        """
        Update a plan's information.
        
        Args:
            plan_id: Primary key of plan to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated Plan instance if found, None otherwise
            
        Raises:
            IntegrityError: If database constraint violated
        """
        try:
            # Update the timestamp
            update_data['updated_at'] = datetime.now()
            
            # Perform the update
            stmt = (
                update(Plan)
                .where(Plan.plan_id == plan_id)
                .values(**update_data)
                .returning(Plan)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update plan", orig=e)

    def delete_plan(self, plan_id: int) -> bool:
        """
        Delete a plan.
        
        Args:
            plan_id: Primary key of plan to delete
            
        Returns:
            True if plan was deleted, False if not found
        """
        stmt = delete(Plan).where(Plan.plan_id == plan_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_plan_summary(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of plan information including counts of related entities.
        
        Args:
            plan_id: Primary key of plan
            
        Returns:
            Dictionary containing plan summary if found, None otherwise
        """
        plan = self.get_plan(plan_id, include_relationships=True)
        if not plan:
            return None
            
        return {
            'plan_id': plan.plan_id,
            'plan_name': plan.plan_name,
            'household_id': plan.household_id,
            'scenario_count': len(plan.scenarios),
            'asset_count': len(plan.assets),
            'liability_count': len(plan.liabilities),
            'cash_flow_count': len(plan.inflows_outflows),
            'retirement_income_count': len(plan.retirement_income_plans),
            'has_base_assumptions': plan.base_assumptions is not None,
            'created_at': plan.created_at,
            'updated_at': plan.updated_at
        }

    def validate_plan_timeline(self, plan_id: int) -> bool:
        """
        Validate that plan's timeline is logically consistent.
        
        Args:
            plan_id: Primary key of plan
            
        Returns:
            True if timeline is valid, False otherwise
        """
        plan = self.get_plan(plan_id)
        if not plan or not plan.base_assumptions:
            return False
            
        # Get required years from base assumptions
        start_year = datetime.now().year  # Plan always starts in current year
        retirement_year = plan.base_assumptions.retirement_age_1  # Using person1's retirement age
        end_year = plan.base_assumptions.final_age_1  # Using person1's final age
        
        return validate_projection_timeline(start_year, retirement_year, end_year)