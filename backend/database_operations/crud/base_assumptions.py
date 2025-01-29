"""
Base assumptions management module.

This module provides CRUD operations for:
- Base retirement assumptions
- Growth and inflation rates
- Age-related settings
"""

from dataclasses import dataclass
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BaseAssumption, Plan

@dataclass
class BaseAssumptionCreate:
    """Data for creating base assumptions."""
    plan_id: int
    retirement_age_1: int
    retirement_age_2: Optional[int] = None
    final_age_1: int = 95
    final_age_2: Optional[int] = None
    final_age_selector: int = 1
    default_growth_rate: float = 0.07
    inflation_rate: float = 0.03

@dataclass
class BaseAssumptionUpdate:
    """Data for updating base assumptions."""
    retirement_age_1: Optional[int] = None
    retirement_age_2: Optional[int] = None
    final_age_1: Optional[int] = None
    final_age_2: Optional[int] = None
    final_age_selector: Optional[int] = None
    default_growth_rate: Optional[float] = None
    inflation_rate: Optional[float] = None

def create_base_assumption(db: Session, assumption_data: BaseAssumptionCreate) -> Optional[BaseAssumption]:
    """Creates base assumptions for a plan."""
    try:
        # Verify plan exists
        plan = db.scalar(select(Plan).where(Plan.plan_id == assumption_data.plan_id))
        if not plan:
            return None
            
        assumption = BaseAssumption(**vars(assumption_data))
        db.add(assumption)
        db.flush()
        return assumption
    except Exception:
        db.rollback()
        raise

def get_base_assumption(db: Session, plan_id: int) -> Optional[BaseAssumption]:
    """Retrieves base assumptions for a plan."""
    try:
        stmt = select(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
        return db.scalar(stmt)
    except Exception:
        db.rollback()
        raise

def update_base_assumption(
    db: Session, 
    plan_id: int, 
    assumption_data: BaseAssumptionUpdate
) -> Optional[BaseAssumption]:
    """Updates base assumptions for a plan."""
    try:
        assumption = get_base_assumption(db, plan_id)
        if not assumption:
            return None
            
        update_data = {k: v for k, v in vars(assumption_data).items() if v is not None}
        for key, value in update_data.items():
            setattr(assumption, key, value)
        
        db.flush()
        return assumption
    except Exception:
        db.rollback()
        raise

def delete_base_assumption(db: Session, plan_id: int) -> bool:
    """Deletes base assumptions for a plan."""
    try:
        assumption = get_base_assumption(db, plan_id)
        if not assumption:
            return False
            
        db.delete(assumption)
        db.flush()
        return True
    except Exception:
        db.rollback()
        raise 