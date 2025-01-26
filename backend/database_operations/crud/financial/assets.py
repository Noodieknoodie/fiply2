"""
Asset management module.

This module provides CRUD operations for:
- Asset categories
- Assets
- Asset-specific validations and business rules
"""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ...models import Asset, AssetCategory

@dataclass
class AssetCategoryCreate:
    """Data transfer object for creating an asset category."""
    plan_id: int
    category_name: str
    category_order: Optional[int] = 0

@dataclass
class AssetCategoryUpdate:
    """Data transfer object for updating an asset category."""
    category_name: Optional[str] = None
    category_order: Optional[int] = None

@dataclass
class AssetCreate:
    """Data transfer object for creating an asset."""
    plan_id: int
    asset_category_id: int
    asset_name: str
    owner: str
    value: float
    include_in_nest_egg: bool = True

@dataclass
class AssetUpdate:
    """Data transfer object for updating an asset."""
    asset_name: Optional[str] = None
    owner: Optional[str] = None
    value: Optional[float] = None
    include_in_nest_egg: Optional[bool] = None
    asset_category_id: Optional[int] = None

def create_asset_category(db: Session, category_data: AssetCategoryCreate) -> AssetCategory:
    """Create a new asset category."""
    # If no order specified, put at end
    if category_data.category_order == 0:
        max_order = db.scalar(
            select(func.max(AssetCategory.category_order))
            .where(AssetCategory.plan_id == category_data.plan_id)
        ) or 0
        category_data.category_order = max_order + 1
    
    db_category = AssetCategory(**vars(category_data))
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_asset_category(db: Session, category_id: int) -> Optional[AssetCategory]:
    """Get a specific asset category by ID."""
    stmt = select(AssetCategory).where(AssetCategory.asset_category_id == category_id)
    return db.scalar(stmt)

def get_plan_asset_categories(db: Session, plan_id: int) -> List[AssetCategory]:
    """Get all asset categories for a plan, ordered by category_order."""
    stmt = (
        select(AssetCategory)
        .where(AssetCategory.plan_id == plan_id)
        .order_by(AssetCategory.category_order)
    )
    return list(db.scalars(stmt))

def update_asset_category(db: Session, category_id: int, category_data: AssetCategoryUpdate) -> Optional[AssetCategory]:
    """Update an asset category's details."""
    stmt = select(AssetCategory).where(AssetCategory.asset_category_id == category_id)
    db_category = db.scalar(stmt)
    if not db_category:
        return None
    
    update_data = {k: v for k, v in vars(category_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_asset_category(db: Session, category_id: int) -> bool:
    """Delete an asset category and all its assets."""
    stmt = select(AssetCategory).where(AssetCategory.asset_category_id == category_id)
    db_category = db.scalar(stmt)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True

def reorder_asset_categories(db: Session, plan_id: int, category_orders: dict[int, int]) -> List[AssetCategory]:
    """Update the order of multiple asset categories."""
    categories = get_plan_asset_categories(db, plan_id)
    for category in categories:
        if category.asset_category_id in category_orders:
            category.category_order = category_orders[category.asset_category_id]
    
    db.commit()
    return get_plan_asset_categories(db, plan_id)

def create_asset(db: Session, asset_data: AssetCreate) -> Asset:
    """Create a new asset."""
    db_asset = Asset(**vars(asset_data))
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_asset(db: Session, asset_id: int) -> Optional[Asset]:
    """Get a specific asset by ID."""
    stmt = select(Asset).where(Asset.asset_id == asset_id)
    return db.scalar(stmt)

def get_category_assets(db: Session, category_id: int) -> List[Asset]:
    """Get all assets in a category."""
    stmt = select(Asset).where(Asset.asset_category_id == category_id)
    return list(db.scalars(stmt))

def get_plan_assets(db: Session, plan_id: int, include_categories: bool = False) -> List[Asset]:
    """Get all assets for a plan."""
    stmt = select(Asset).where(Asset.plan_id == plan_id)
    
    if include_categories:
        stmt = stmt.join(Asset.category)
        
    return list(db.scalars(stmt).unique())

def update_asset(db: Session, asset_id: int, asset_data: AssetUpdate) -> Optional[Asset]:
    """Update an asset's details."""
    stmt = select(Asset).where(Asset.asset_id == asset_id)
    db_asset = db.scalar(stmt)
    if not db_asset:
        return None
    
    update_data = {k: v for k, v in vars(asset_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_asset, key, value)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset

def delete_asset(db: Session, asset_id: int) -> bool:
    """Delete an asset."""
    stmt = select(Asset).where(Asset.asset_id == asset_id)
    db_asset = db.scalar(stmt)
    if not db_asset:
        return False
    
    db.delete(db_asset)
    db.commit()
    return True 