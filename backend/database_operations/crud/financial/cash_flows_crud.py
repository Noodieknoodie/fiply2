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
from ...validation.time_validation import validate_year_not_before_plan_creation
from ...utils.time_utils import get_years_between


class CashFlowCRUD:
    """Handles CRUD operations for inflow/outflow management."""

    def __init__(self, session: Session):
        self.session = session

    def create_cash_flow(self, plan_id: int, name: str, flow_type: str, annual_amount: float, start_year: int,
                         end_year: Optional[int] = None, apply_inflation: bool = False) -> InflowOutflow:
        """Creates a cash flow event for a financial plan."""
        plan = self.session.execute(select(Plan).where(Plan.plan_id == plan_id)).scalar_one_or_none()
        if not plan:
            raise NoResultFound(f"Plan {plan_id} not found")

        if flow_type not in {"inflow", "outflow"}:
            raise ValueError("Type must be 'inflow' or 'outflow'")

        validate_positive_amount(annual_amount, "annual_amount")

        end_year = end_year or start_year
        if not validate_year_not_before_plan_creation(start_year, plan.plan_creation_year):
            raise ValueError("Start year cannot be before plan creation year")
        if start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")
        if get_years_between(start_year, end_year) > 30:
            raise ValueError("Cash flows must be limited duration events")

        cash_flow = InflowOutflow(
            plan_id=plan_id, name=name, type=flow_type, annual_amount=annual_amount,
            start_year=start_year, end_year=end_year, apply_inflation=apply_inflation
        )

        try:
            self.session.add(cash_flow)
            self.session.commit()
            return cash_flow
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create cash flow", orig=e)

    def get_cash_flow(self, flow_id: int) -> Optional[InflowOutflow]:
        """Retrieves a cash flow by ID."""
        return self.session.execute(select(InflowOutflow).where(
            InflowOutflow.inflow_outflow_id == flow_id)).scalar_one_or_none()

    def get_plan_cash_flows(self, plan_id: int, flow_type: Optional[str] = None,
                            year: Optional[int] = None) -> List[InflowOutflow]:
        """Retrieves cash flows for a plan, optionally filtered by type and year."""
        stmt = select(InflowOutflow).where(InflowOutflow.plan_id == plan_id)
        if flow_type:
            stmt = stmt.where(InflowOutflow.type == flow_type)
        if year:
            stmt = stmt.where(InflowOutflow.start_year <= year, InflowOutflow.end_year >= year)
        return list(self.session.execute(stmt).scalars().all())

    def update_cash_flow(self, flow_id: int, update_data: Dict[str, Any]) -> Optional[InflowOutflow]:
        """Updates a cash flow event."""
        if "annual_amount" in update_data:
            validate_positive_amount(update_data["annual_amount"], "annual_amount")
        if "type" in update_data and update_data["type"] not in {"inflow", "outflow"}:
            raise ValueError("Type must be 'inflow' or 'outflow'")

        if "start_year" in update_data or "end_year" in update_data:
            current_flow = self.get_cash_flow(flow_id)
            if not current_flow:
                return None

            start_year = update_data.get("start_year", current_flow.start_year)
            end_year = update_data.get("end_year", current_flow.end_year)

            if start_year > end_year:
                raise ValueError("Start year must be before or equal to end year")
            if end_year - start_year > 30:
                raise ValueError("Cash flows must be limited duration events")

        try:
            result = self.session.execute(update(InflowOutflow)
                                          .where(InflowOutflow.inflow_outflow_id == flow_id)
                                          .values(**update_data)
                                          .returning(InflowOutflow))
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update cash flow", orig=e)

    def delete_cash_flow(self, flow_id: int) -> bool:
        """Deletes a cash flow event."""
        result = self.session.execute(delete(InflowOutflow).where(
            InflowOutflow.inflow_outflow_id == flow_id))
        self.session.commit()
        return result.rowcount > 0
