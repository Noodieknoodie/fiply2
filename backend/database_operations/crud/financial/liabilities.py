"""
Liability management module.

This module provides CRUD operations for:
- Liability categories
- Liabilities
- Interest rate calculations and validations
"""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ...models import Liability, LiabilityCategory

@dataclass
class LiabilityCategoryCreate:
    """Data transfer object for creating a liability category."""
    plan_id: int
    category_name: str
    category_order: Optional[int] = 0

@dataclass
class LiabilityCategoryUpdate:
    """Data transfer object for updating a liability category."""
    category_name: Optional[str] = None
    category_order: Optional[int] = None

@dataclass
class LiabilityCreate:
    """Data transfer object for creating a liability."""
    plan_id: int
    liability_category_id: int
    liability_name: str
    owner: str
    value: float
    interest_rate: Optional[float] = None
    include_in_nest_egg: bool = True

@dataclass
class LiabilityUpdate:
    """Data transfer object for updating a liability."""
    liability_name: Optional[str] = None
    owner: Optional[str] = None
    value: Optional[float] = None
    interest_rate: Optional[float] = None
    include_in_nest_egg: Optional[bool] = None
    liability_category_id: Optional[int] = None

def create_liability_category(db: Session, category_data: LiabilityCategoryCreate) -> LiabilityCategory:
    """Create a new liability category."""
    if category_data.category_order == 0:
        max_order = db.scalar(
            select(func.max(LiabilityCategory.category_order))
            .where(LiabilityCategory.plan_id == category_data.plan_id)
        ) or 0
        category_data.category_order = max_order + 1
    
    db_category = LiabilityCategory(**vars(category_data))
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_liability_category(db: Session, category_id: int) -> Optional[LiabilityCategory]:
    """Get a specific liability category by ID."""
    stmt = select(LiabilityCategory).where(LiabilityCategory.liability_category_id == category_id)
    return db.scalar(stmt)

def get_plan_liability_categories(db: Session, plan_id: int) -> List[LiabilityCategory]:
    """Get all liability categories for a plan, ordered by category_order."""
    stmt = (
        select(LiabilityCategory)
        .where(LiabilityCategory.plan_id == plan_id)
        .order_by(LiabilityCategory.category_order)
    )
    return list(db.scalars(stmt))

def update_liability_category(db: Session, category_id: int, category_data: LiabilityCategoryUpdate) -> Optional[LiabilityCategory]:
    """Update a liability category's details."""
    stmt = select(LiabilityCategory).where(LiabilityCategory.liability_category_id == category_id)
    db_category = db.scalar(stmt)
    if not db_category:
        return None
    
    update_data = {k: v for k, v in vars(category_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_liability_category(db: Session, category_id: int) -> bool:
    """Delete a liability category and all its liabilities."""
    stmt = select(LiabilityCategory).where(LiabilityCategory.liability_category_id == category_id)
    db_category = db.scalar(stmt)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True

def reorder_liability_categories(db: Session, plan_id: int, category_orders: dict[int, int]) -> List[LiabilityCategory]:
    """Update the order of multiple liability categories."""
    categories = get_plan_liability_categories(db, plan_id)
    for category in categories:
        if category.liability_category_id in category_orders:
            category.category_order = category_orders[category.liability_category_id]
    
    db.commit()
    return get_plan_liability_categories(db, plan_id)

def create_liability(db: Session, liability_data: LiabilityCreate) -> Liability:
    """Create a new liability."""
    db_liability = Liability(**vars(liability_data))
    db.add(db_liability)
    db.commit()
    db.refresh(db_liability)
    return db_liability

def get_liability(db: Session, liability_id: int) -> Optional[Liability]:
    """Get a specific liability by ID."""
    stmt = select(Liability).where(Liability.liability_id == liability_id)
    return db.scalar(stmt)

def get_category_liabilities(db: Session, category_id: int) -> List[Liability]:
    """Get all liabilities in a category."""
    stmt = select(Liability).where(Liability.liability_category_id == category_id)
    return list(db.scalars(stmt))

def get_plan_liabilities(db: Session, plan_id: int, include_categories: bool = False) -> List[Liability]:
    """Get all liabilities for a plan."""
    stmt = select(Liability).where(Liability.plan_id == plan_id)
    
    if include_categories:
        stmt = stmt.join(Liability.category)
        
    return list(db.scalars(stmt).unique())

def update_liability(db: Session, liability_id: int, liability_data: LiabilityUpdate) -> Optional[Liability]:
    """Update a liability's details."""
    stmt = select(Liability).where(Liability.liability_id == liability_id)
    db_liability = db.scalar(stmt)
    if not db_liability:
        return None
    
    update_data = {k: v for k, v in vars(liability_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_liability, key, value)
    
    db.commit()
    db.refresh(db_liability)
    return db_liability

def delete_liability(db: Session, liability_id: int) -> bool:
    """Delete a liability."""
    stmt = select(Liability).where(Liability.liability_id == liability_id)
    db_liability = db.scalar(stmt)
    if not db_liability:
        return False
    
    db.delete(db_liability)
    db.commit()
    return True 