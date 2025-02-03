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
from ..validation.scenario_timeline_validation import validate_projection_timeline

class PlanCRUD:
    """Handles CRUD operations for financial plans."""

    def __init__(self, session: Session):
        self.session = session

    def create_plan(self, household_id: int, plan_name: str) -> Plan:
        """Creates a financial plan for a household."""
        if not self.session.execute(select(Household).where(Household.household_id == household_id)).scalar_one_or_none():
            raise NoResultFound(f"Household {household_id} not found")

        plan = Plan(household_id=household_id, plan_name=plan_name)

        try:
            self.session.add(plan)
            self.session.commit()
            return plan
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create plan", orig=e)

    def get_plan(self, plan_id: int, include_relationships: bool = False) -> Optional[Plan]:
        """Retrieves a plan by ID, optionally loading related data."""
        stmt = select(Plan).where(Plan.plan_id == plan_id)
        if include_relationships:
            stmt = stmt.options(
                joinedload(Plan.base_assumptions), joinedload(Plan.scenarios),
                joinedload(Plan.asset_categories), joinedload(Plan.liability_categories),
                joinedload(Plan.assets), joinedload(Plan.liabilities),
                joinedload(Plan.inflows_outflows), joinedload(Plan.retirement_income_plans)
            )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_household_plans(self, household_id: int) -> List[Plan]:
        """Returns all plans for a household."""
        return list(self.session.execute(select(Plan).where(Plan.household_id == household_id)).scalars().all())

    def update_plan(self, plan_id: int, update_data: Dict[str, Any]) -> Optional[Plan]:
        """Updates a financial plan."""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.session.execute(
                update(Plan).where(Plan.plan_id == plan_id).values(**update_data).returning(Plan)
            )
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update plan", orig=e)

    def delete_plan(self, plan_id: int) -> bool:
        """Deletes a plan by ID."""
        result = self.session.execute(delete(Plan).where(Plan.plan_id == plan_id))
        self.session.commit()
        return result.rowcount > 0

    def get_plan_summary(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Returns a summary of a plan including related entity counts."""
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
        """Validates if a plan's timeline is logically consistent."""
        plan = self.get_plan(plan_id)
        if not plan or not plan.base_assumptions:
            return False

        start_year = datetime.now().year
        return validate_projection_timeline(
            start_year, plan.base_assumptions.retirement_age_1, plan.base_assumptions.final_age_1
        )
