# backend/database_operations/crud/financial/cash_flows.py
"""
Full CRUD operations for cash flows following SQLAlchemy 2.0 style
Support for both inflows and outflows
Proper validation of:
Flow amounts (positive)
Flow types
Owner values
Timeline consistency
Support for filtering flows by:
Type (inflow/outflow)
Active in specific year
Comprehensive flow summary including:
Duration calculation
Single-year event detection
Total nominal amount
Additional utility for calculating year totals
Proper error handling and transaction management
Support for inflation toggle
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import InflowOutflow, Plan
from ...utils.money_validations import validate_positive_amount
from ...utils.time_validations import (
    validate_projection_timeline,
    is_within_projection_period
)

class CashFlowCRUD:
    """CRUD operations for inflow/outflow management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_cash_flow(
        self,
        plan_id: int,
        flow_type: str,
        name: str,
        annual_amount: float,
        start_year: int,
        owner: str,
        end_year: Optional[int] = None,
        apply_inflation: bool = False
    ) -> InflowOutflow:
        """
        Create a new cash flow (inflow or outflow).
        
        Args:
            plan_id: ID of plan this cash flow belongs to
            flow_type: Type of flow ('inflow' or 'outflow')
            name: Name identifier for the cash flow
            annual_amount: Annual amount of the flow
            start_year: Year the flow begins
            owner: Owner of the flow ('person1', 'person2', or 'joint')
            end_year: Optional year the flow ends (same as start_year if None)
            apply_inflation: Whether to apply inflation adjustments
            
        Returns:
            Newly created InflowOutflow instance
            
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

        # Validate input
        if flow_type not in ['inflow', 'outflow']:
            raise ValueError("Invalid flow type")
        
        validate_positive_amount(annual_amount, "annual_amount")
        
        if owner not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        # If end_year not provided, set to start_year (single-year event)
        end_year = end_year or start_year

        # Validate timeline
        if start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")

        # Create cash flow instance
        cash_flow = InflowOutflow(
            plan_id=plan_id,
            type=flow_type,
            name=name,
            annual_amount=annual_amount,
            start_year=start_year,
            end_year=end_year,
            owner=owner,
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
        """
        Retrieve a cash flow by ID.
        
        Args:
            flow_id: Primary key of cash flow
            
        Returns:
            InflowOutflow instance if found, None otherwise
        """
        stmt = select(InflowOutflow).where(InflowOutflow.inflow_outflow_id == flow_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_cash_flows(
        self,
        plan_id: int,
        flow_type: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[InflowOutflow]:
        """
        Retrieve cash flows for a plan, optionally filtered by type and year.
        
        Args:
            plan_id: ID of plan to get cash flows for
            flow_type: Optional type to filter by ('inflow' or 'outflow')
            year: Optional year to check for active flows
            
        Returns:
            List of InflowOutflow instances
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
            flow_id: Primary key of cash flow to update
            update_data: Dictionary of fields to update and their new values
            
        Returns:
            Updated InflowOutflow instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate amount if included in update
        if 'annual_amount' in update_data:
            validate_positive_amount(update_data['annual_amount'], "annual_amount")

        # Validate flow type if included
        if 'type' in update_data and update_data['type'] not in ['inflow', 'outflow']:
            raise ValueError("Invalid flow type")

        # Validate owner if included
        if 'owner' in update_data and update_data['owner'] not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        # Validate timeline if updating years
        if 'start_year' in update_data or 'end_year' in update_data:
            current_flow = self.get_cash_flow(flow_id)
            if not current_flow:
                return None
                
            start_year = update_data.get('start_year', current_flow.start_year)
            end_year = update_data.get('end_year', current_flow.end_year)
            
            if start_year > end_year:
                raise ValueError("Start year must be before or equal to end year")

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
        """
        Delete a cash flow.
        
        Args:
            flow_id: Primary key of cash flow to delete
            
        Returns:
            True if cash flow was deleted, False if not found
        """
        stmt = delete(InflowOutflow).where(InflowOutflow.inflow_outflow_id == flow_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_cash_flow_summary(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of cash flow information.
        
        Args:
            flow_id: Primary key of cash flow
            
        Returns:
            Dictionary containing cash flow summary if found, None otherwise
        """
        cash_flow = self.get_cash_flow(flow_id)
        if not cash_flow:
            return None
            
        duration = cash_flow.end_year - cash_flow.start_year + 1
            
        return {
            'flow_id': cash_flow.inflow_outflow_id,
            'name': cash_flow.name,
            'type': cash_flow.type,
            'annual_amount': cash_flow.annual_amount,
            'start_year': cash_flow.start_year,
            'end_year': cash_flow.end_year,
            'owner': cash_flow.owner,
            'apply_inflation': cash_flow.apply_inflation,
            'duration_years': duration,
            'is_single_year': duration == 1,
            'total_nominal_amount': cash_flow.annual_amount * duration
        }

    def get_year_totals(
        self,
        plan_id: int,
        year: int,
        include_inflation: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total inflows and outflows for a specific year.
        
        Args:
            plan_id: ID of plan to calculate totals for
            year: Year to calculate totals for
            include_inflation: Whether to include inflation-adjusted amounts
            
        Returns:
            Dictionary with total inflows and outflows for the year
        """
        active_flows = self.get_plan_cash_flows(plan_id, year=year)
        
        totals = {
            'inflows': 0.0,
            'outflows': 0.0,
            'net_flow': 0.0
        }
        
        for flow in active_flows:
            if flow.type == 'inflow':
                totals['inflows'] += flow.annual_amount
            else:
                totals['outflows'] += flow.annual_amount
                
        totals['net_flow'] = totals['inflows'] - totals['outflows']
        
        return totals