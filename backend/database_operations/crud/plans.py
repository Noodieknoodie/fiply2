from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Plan, BaseAssumption

@dataclass
class PlanCreate:
    """Data transfer object for creating a new plan."""
    household_id: int
    plan_name: str
    description: Optional[str] = None
    target_fire_age: Optional[int] = None
    target_fire_amount: Optional[float] = None
    risk_tolerance: Optional[str] = None

@dataclass
class PlanUpdate:
    """Data transfer object for updating an existing plan."""
    plan_name: Optional[str] = None
    description: Optional[str] = None
    target_fire_age: Optional[int] = None
    target_fire_amount: Optional[float] = None
    risk_tolerance: Optional[str] = None
    is_active: Optional[bool] = None

@dataclass
class BaseAssumptionCreate:
    """Data transfer object for creating base assumptions."""
    plan_id: int
    retirement_age_1: Optional[int] = None
    retirement_age_2: Optional[int] = None
    final_age_1: Optional[int] = None
    final_age_2: Optional[int] = None
    final_age_selector: Optional[int] = None
    default_growth_rate: Optional[float] = None
    inflation_rate: Optional[float] = None

@dataclass
class BaseAssumptionUpdate:
    """Data transfer object for updating base assumptions."""
    retirement_age_1: Optional[int] = None
    retirement_age_2: Optional[int] = None
    final_age_1: Optional[int] = None
    final_age_2: Optional[int] = None
    final_age_selector: Optional[int] = None
    default_growth_rate: Optional[float] = None
    inflation_rate: Optional[float] = None

def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
    """Create a new financial plan."""
    db_plan = Plan(**vars(plan_data))
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_plan(db: Session, plan_id: int) -> Optional[Plan]:
    """Get a specific plan by ID."""
    stmt = select(Plan).where(Plan.plan_id == plan_id)
    return db.scalar(stmt)

def get_household_plans(
    db: Session, 
    household_id: int, 
    skip: int = 0, 
    limit: int = 100,
    include_inactive: bool = False
) -> List[Plan]:
    """Get all plans for a specific household with pagination."""
    stmt = select(Plan).where(Plan.household_id == household_id)
    if not include_inactive:
        stmt = stmt.where(Plan.is_active == True)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).unique())

def update_plan(db: Session, plan_id: int, plan_data: PlanUpdate) -> Optional[Plan]:
    """Update a plan's details."""
    stmt = select(Plan).where(Plan.plan_id == plan_id)
    db_plan = db.scalar(stmt)
    if not db_plan:
        return None
    
    update_data = {k: v for k, v in vars(plan_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db_plan.updated_at = datetime.now()
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int) -> bool:
    """Delete a plan."""
    stmt = select(Plan).where(Plan.plan_id == plan_id)
    db_plan = db.scalar(stmt)
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True

def create_base_assumptions(db: Session, assumptions_data: BaseAssumptionCreate) -> BaseAssumption:
    """Create base assumptions for a plan."""
    db_assumptions = BaseAssumption(**vars(assumptions_data))
    db.add(db_assumptions)
    db.commit()
    db.refresh(db_assumptions)
    return db_assumptions

def get_plan_assumptions(db: Session, plan_id: int) -> Optional[BaseAssumption]:
    """Get base assumptions for a specific plan."""
    stmt = select(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
    return db.scalar(stmt)

def update_base_assumptions(
    db: Session, 
    plan_id: int, 
    assumptions_data: BaseAssumptionUpdate
) -> Optional[BaseAssumption]:
    """Update base assumptions for a plan."""
    stmt = select(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
    db_assumptions = db.scalar(stmt)
    if not db_assumptions:
        return None
    
    update_data = {k: v for k, v in vars(assumptions_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_assumptions, key, value)
    
    db.commit()
    db.refresh(db_assumptions)
    return db_assumptions

def delete_base_assumptions(db: Session, plan_id: int) -> bool:
    """Delete base assumptions for a plan."""
    stmt = select(BaseAssumption).where(BaseAssumption.plan_id == plan_id)
    db_assumptions = db.scalar(stmt)
    if not db_assumptions:
        return False
    
    db.delete(db_assumptions)
    db.commit()
    return True 