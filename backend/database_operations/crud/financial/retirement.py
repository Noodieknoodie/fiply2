"""
Retirement income plan management module.

This module provides CRUD operations for retirement income sources such as:
- Social Security benefits
- Pension payments
- Other retirement income streams
"""

from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ...models import RetirementIncomePlan, Plan

@dataclass
class RetirementIncomePlanCreate:
    """Data for creating a new retirement income plan."""
    plan_id: int
    name: str
    owner: str
    annual_income: float
    start_age: int
    end_age: Optional[int] = None
    include_in_nest_egg: bool = True
    apply_inflation: bool = True

@dataclass
class RetirementIncomePlanUpdate:
    """Data for updating an existing retirement income plan."""
    name: Optional[str] = None
    owner: Optional[str] = None
    annual_income: Optional[float] = None
    start_age: Optional[int] = None
    end_age: Optional[int] = None
    include_in_nest_egg: Optional[bool] = None
    apply_inflation: Optional[bool] = None

def create_retirement_plan(db: Session, plan_data: RetirementIncomePlanCreate) -> Optional[RetirementIncomePlan]:
    """Creates a new retirement income plan."""
    try:
        # Verify plan exists
        plan = db.scalar(select(Plan).where(Plan.plan_id == plan_data.plan_id))
        if not plan:
            return None
            
        # Convert bools to int for SQLite
        data_dict = vars(plan_data)
        data_dict['include_in_nest_egg'] = 1 if data_dict['include_in_nest_egg'] else 0
        data_dict['apply_inflation'] = 1 if data_dict['apply_inflation'] else 0
        
        retirement_plan = RetirementIncomePlan(**data_dict)
        db.add(retirement_plan)
        db.flush()
        return retirement_plan
    except Exception:
        db.rollback()
        raise

def get_retirement_plan(db: Session, income_plan_id: int) -> Optional[RetirementIncomePlan]:
    """Retrieves a specific retirement income plan by ID."""
    try:
        stmt = (
            select(RetirementIncomePlan)
            .options(joinedload(RetirementIncomePlan.plan))
            .where(RetirementIncomePlan.income_plan_id == income_plan_id)
        )
        return db.scalar(stmt)
    except Exception:
        db.rollback()
        raise

def get_plan_retirement_plans(db: Session, plan_id: int) -> List[RetirementIncomePlan]:
    """Retrieves all retirement income plans for a plan."""
    try:
        stmt = (
            select(RetirementIncomePlan)
            .where(RetirementIncomePlan.plan_id == plan_id)
        )
        return list(db.scalars(stmt).unique())
    except Exception:
        db.rollback()
        raise

def update_retirement_plan(
    db: Session, 
    income_plan_id: int, 
    plan_data: RetirementIncomePlanUpdate
) -> Optional[RetirementIncomePlan]:
    """Updates an existing retirement income plan."""
    try:
        retirement_plan = get_retirement_plan(db, income_plan_id)
        if not retirement_plan:
            return None
            
        update_data = {k: v for k, v in vars(plan_data).items() if v is not None}
        
        # Convert bools to int for SQLite if present
        if 'include_in_nest_egg' in update_data:
            update_data['include_in_nest_egg'] = 1 if update_data['include_in_nest_egg'] else 0
        if 'apply_inflation' in update_data:
            update_data['apply_inflation'] = 1 if update_data['apply_inflation'] else 0
            
        for key, value in update_data.items():
            setattr(retirement_plan, key, value)
        
        db.flush()
        return retirement_plan
    except Exception:
        db.rollback()
        raise

def delete_retirement_plan(db: Session, income_plan_id: int) -> bool:
    """Deletes a retirement income plan."""
    try:
        retirement_plan = get_retirement_plan(db, income_plan_id)
        if not retirement_plan:
            return False
            
        db.delete(retirement_plan)
        db.flush()
        return True
    except Exception:
        db.rollback()
        raise 