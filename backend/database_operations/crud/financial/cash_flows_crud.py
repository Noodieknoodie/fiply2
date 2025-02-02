# backend/database_operations/crud/financial/cash_flows_crud.py
"""
Full CRUD operations for cash flows following SQLAlchemy 2.0 style.
Handles discrete event cash flows (like college expenses or inheritances).

Core functionality:
- Create/update/delete cash flows
- Basic validation
- Support for single-year and multi-year discrete events
- Optional inflation adjustment
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import InflowOutflow, Plan
from ...validation.money_validation import validate_positive_amount

class CashFlowCRUD:
    """CRUD operations for inflow/outflow management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_cash_flow(
        self,
        plan_id: int,
        name: str,
        flow_type: str,
        annual_amount: float,
        start_year: int,
        end_year: Optional[int] = None,
        apply_inflation: bool = False
    ) -> InflowOutflow:
        """
        Create a discrete event cash flow.
        
        Args:
            plan_id: ID of plan this flow belongs to
            name: Name of the cash flow (e.g., "College Tuition")
            flow_type: Type of flow ('inflow' or 'outflow')
            annual_amount: Annual amount of the flow
            start_year: Year the flow begins
            end_year: Optional year the flow ends (same as start_year if None)
            apply_inflation: Whether to apply inflation adjustments
            
        Returns:
            Newly created InflowOutflow instance
            
        Raises:
            ValueError: If validation fails
            NoResultFound: If plan_id doesn't exist
        """
        # Verify plan exists and get its start year
        plan = self.session.execute(
            select(Plan).where(Plan.plan_id == plan_id)
        ).scalar_one_or_none()
        
        if not plan:
            raise NoResultFound(f"Plan {plan_id} not found")

        # Validate input
        if flow_type not in ['inflow', 'outflow']:
            raise ValueError("Type must be 'inflow' or 'outflow'")
        
        validate_positive_amount(annual_amount, "annual_amount")
        
        # Handle single-year events
        actual_end_year = end_year or start_year
        
        # Validate it's a discrete event
        if actual_end_year - start_year > 30:  # reasonable max for discrete events
            raise ValueError("Cash flows must be discrete events (limited duration)")
            
        # Validate against plan timeline
        if start_year < plan.plan_creation_year:
            raise ValueError("Cannot start before plan creation year")
            
        if start_year > actual_end_year:
            raise ValueError("Start year must be before or equal to end year")

        # Create cash flow instance
        cash_flow = InflowOutflow(
            plan_id=plan_id,
            name=name,
            type=flow_type,
            annual_amount=annual_amount,
            start_year=start_year,
            end_year=actual_end_year,
            apply_inflation=apply_inflation
        )
        
        try:
            self.session.add(cash_flow)
            self.session.commit()
            return cash_flow
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create cash flow", orig=e)

    def get_cash_flow(self, flow_id: int) -> Optional[InflowOutflow]:
        """Get a cash flow by ID."""
        stmt = select(InflowOutflow).where(InflowOutflow.inflow_outflow_id == flow_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_cash_flows(
        self,
        plan_id: int,
        flow_type: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[InflowOutflow]:
        """
        Get cash flows for a plan, optionally filtered by type and year.
        
        Args:
            plan_id: ID of plan to get flows for
            flow_type: Optional type to filter by ('inflow' or 'outflow')
            year: Optional year to check for active flows
        """
        stmt = select(InflowOutflow).where(InflowOutflow.plan_id == plan_id)
        
        if flow_type:
            stmt = stmt.where(InflowOutflow.type == flow_type)
            
        if year is not None:
            stmt = stmt.where(
                InflowOutflow.start_year <= year,
                InflowOutflow.end_year >= year
            )
            
        return list(self.session.execute(stmt).scalars().all())

    def update_cash_flow(
        self,
        flow_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[InflowOutflow]:
        """
        Update a cash flow.
        
        Args:
            flow_id: ID of flow to update
            update_data: Dictionary of fields to update
        """
        # Validate amount if included
        if 'annual_amount' in update_data:
            validate_positive_amount(update_data['annual_amount'], "annual_amount")

        # Validate flow type if included
        if 'type' in update_data and update_data['type'] not in ['inflow', 'outflow']:
            raise ValueError("Type must be 'inflow' or 'outflow'")

        # Validate timeline if updating years
        if 'start_year' in update_data or 'end_year' in update_data:
            current_flow = self.get_cash_flow(flow_id)
            if not current_flow:
                return None
                
            start_year = update_data.get('start_year', current_flow.start_year)
            end_year = update_data.get('end_year', current_flow.end_year)
            
            if start_year > end_year:
                raise ValueError("Start year must be before or equal to end year")

            # Validate discrete event
            if end_year - start_year > 30:
                raise ValueError("Cash flows must be discrete events (limited duration)")

        try:
            stmt = (
                update(InflowOutflow)
                .where(InflowOutflow.inflow_outflow_id == flow_id)
                .values(**update_data)
                .returning(InflowOutflow)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update cash flow", orig=e)

    def delete_cash_flow(self, flow_id: int) -> bool:
        """Delete a cash flow."""
        stmt = delete(InflowOutflow).where(InflowOutflow.inflow_outflow_id == flow_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0