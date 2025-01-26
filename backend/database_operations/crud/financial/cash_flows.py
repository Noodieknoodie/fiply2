"""
Cash flow management module.

This module provides CRUD operations for:
- Inflows (income sources)
- Outflows (expenses)
- Date range and inflation adjustments
"""

from datetime import date
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ...models import InflowOutflow, Plan

@dataclass
class InflowOutflowCreate:
    """Data for creating a new inflow or outflow."""
    plan_id: int
    type: str  # 'inflow' or 'outflow'
    name: str
    annual_amount: float
    start_date: date
    end_date: Optional[date] = None
    apply_inflation: bool = False

@dataclass
class InflowOutflowUpdate:
    """Data for updating an existing inflow or outflow."""
    name: Optional[str] = None
    annual_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    apply_inflation: Optional[bool] = None

def create_inflow_outflow(db: Session, cash_flow_data: InflowOutflowCreate) -> Optional[InflowOutflow]:
    """Creates a new inflow or outflow."""
    try:
        # Verify plan exists
        plan = db.scalar(select(Plan).where(Plan.plan_id == cash_flow_data.plan_id))
        if not plan:
            return None
            
        # Convert bool to int for SQLite
        data_dict = vars(cash_flow_data)
        data_dict['apply_inflation'] = 1 if data_dict['apply_inflation'] else 0
        
        cash_flow = InflowOutflow(**data_dict)
        db.add(cash_flow)
        db.flush()
        return cash_flow
    except Exception:
        db.rollback()
        raise

def get_inflow_outflow(db: Session, inflow_outflow_id: int) -> Optional[InflowOutflow]:
    """Retrieves a specific inflow or outflow by ID."""
    try:
        stmt = (
            select(InflowOutflow)
            .options(joinedload(InflowOutflow.plan))
            .where(InflowOutflow.inflow_outflow_id == inflow_outflow_id)
        )
        return db.scalar(stmt)
    except Exception:
        db.rollback()
        raise

def get_plan_cash_flows(db: Session, plan_id: int, flow_type: Optional[str] = None) -> List[InflowOutflow]:
    """Retrieves all cash flows for a plan, optionally filtered by type."""
    try:
        stmt = (
            select(InflowOutflow)
            .where(InflowOutflow.plan_id == plan_id)
        )
        if flow_type:
            stmt = stmt.where(InflowOutflow.type == flow_type)
        return list(db.scalars(stmt).unique())
    except Exception:
        db.rollback()
        raise

def update_inflow_outflow(db: Session, inflow_outflow_id: int, cash_flow_data: InflowOutflowUpdate) -> Optional[InflowOutflow]:
    """Updates an existing inflow or outflow."""
    try:
        cash_flow = get_inflow_outflow(db, inflow_outflow_id)
        if not cash_flow:
            return None
            
        update_data = {k: v for k, v in vars(cash_flow_data).items() if v is not None}
        
        # Convert bool to int for SQLite if present
        if 'apply_inflation' in update_data:
            update_data['apply_inflation'] = 1 if update_data['apply_inflation'] else 0
            
        for key, value in update_data.items():
            setattr(cash_flow, key, value)
        
        db.flush()
        return cash_flow
    except Exception:
        db.rollback()
        raise

def delete_inflow_outflow(db: Session, inflow_outflow_id: int) -> bool:
    """Deletes an inflow or outflow."""
    try:
        cash_flow = get_inflow_outflow(db, inflow_outflow_id)
        if not cash_flow:
            return False
            
        db.delete(cash_flow)
        db.flush()
        return True
    except Exception:
        db.rollback()
        raise 