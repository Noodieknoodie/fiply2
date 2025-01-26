"""
Growth rate configuration module.

This module provides CRUD operations for:
- Default growth rates
- Scenario-specific overrides
- Time-based rate configurations
"""

from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...models import GrowthRateConfiguration, Asset, RetirementIncomePlan

@dataclass
class GrowthRateCreate:
    configuration_type: str
    growth_rate: float
    asset_id: Optional[int] = None
    retirement_income_plan_id: Optional[int] = None
    scenario_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

@dataclass
class GrowthRateUpdate:
    configuration_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    growth_rate: Optional[float] = None

def create_growth_rate(db: Session, growth_rate_data: GrowthRateCreate) -> GrowthRateConfiguration:
    """Creates a new growth rate configuration."""
    # Validate configuration type
    valid_types = ['DEFAULT', 'OVERRIDE', 'STEPWISE']
    if growth_rate_data.configuration_type not in valid_types:
        raise ValueError(f"Invalid configuration_type. Must be one of: {valid_types}")

    # For stepwise configurations, ensure dates are provided
    if growth_rate_data.configuration_type == 'STEPWISE':
        if not growth_rate_data.start_date or not growth_rate_data.end_date:
            raise ValueError("Stepwise configurations require both start_date and end_date")

    # Create the growth rate configuration
    growth_rate = GrowthRateConfiguration(**vars(growth_rate_data))
    db.add(growth_rate)
    db.flush()
    return growth_rate

def get_growth_rate(db: Session, growth_rate_id: int) -> Optional[GrowthRateConfiguration]:
    """Retrieves a growth rate configuration by ID."""
    return db.scalar(
        select(GrowthRateConfiguration)
        .where(GrowthRateConfiguration.growth_rate_id == growth_rate_id)
    )

def get_asset_growth_rates(db: Session, asset_id: int) -> List[GrowthRateConfiguration]:
    """Retrieves all growth rate configurations for an asset."""
    return list(db.scalars(
        select(GrowthRateConfiguration)
        .where(GrowthRateConfiguration.asset_id == asset_id)
        .order_by(GrowthRateConfiguration.start_date)
    ))

def get_retirement_plan_growth_rates(db: Session, retirement_plan_id: int) -> List[GrowthRateConfiguration]:
    """Retrieves all growth rate configurations for a retirement income plan."""
    return list(db.scalars(
        select(GrowthRateConfiguration)
        .where(GrowthRateConfiguration.retirement_income_plan_id == retirement_plan_id)
        .order_by(GrowthRateConfiguration.start_date)
    ))

def get_scenario_growth_rates(db: Session, scenario_id: int) -> List[GrowthRateConfiguration]:
    """Retrieves all growth rate configurations for a scenario."""
    return list(db.scalars(
        select(GrowthRateConfiguration)
        .where(GrowthRateConfiguration.scenario_id == scenario_id)
        .order_by(GrowthRateConfiguration.start_date)
    ))

def update_growth_rate(
    db: Session, 
    growth_rate_id: int, 
    growth_rate_data: GrowthRateUpdate
) -> Optional[GrowthRateConfiguration]:
    """Updates a growth rate configuration."""
    growth_rate = get_growth_rate(db, growth_rate_id)
    if not growth_rate:
        return None

    # Update only provided fields
    update_data = {k: v for k, v in vars(growth_rate_data).items() if v is not None}
    
    # Validate configuration type if provided
    if 'configuration_type' in update_data:
        valid_types = ['DEFAULT', 'OVERRIDE', 'STEPWISE']
        if update_data['configuration_type'] not in valid_types:
            raise ValueError(f"Invalid configuration_type. Must be one of: {valid_types}")

    for key, value in update_data.items():
        setattr(growth_rate, key, value)

    db.flush()
    return growth_rate

def delete_growth_rate(db: Session, growth_rate_id: int) -> bool:
    """Deletes a growth rate configuration."""
    growth_rate = get_growth_rate(db, growth_rate_id)
    if not growth_rate:
        return False
    
    db.delete(growth_rate)
    db.flush()
    return True 