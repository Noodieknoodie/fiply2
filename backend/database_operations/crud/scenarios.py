from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Scenario, ScenarioAssumption

@dataclass
class ScenarioCreate:
    """Data transfer object for creating a new scenario."""
    plan_id: int
    scenario_name: str
    scenario_color: Optional[str] = None

@dataclass
class ScenarioUpdate:
    """Data transfer object for updating a scenario."""
    scenario_name: Optional[str] = None
    scenario_color: Optional[str] = None

@dataclass
class ScenarioAssumptionCreate:
    """Data transfer object for creating scenario assumptions."""
    scenario_id: int
    retirement_age_1: Optional[int] = None
    retirement_age_2: Optional[int] = None
    default_growth_rate: Optional[float] = None
    inflation_rate: Optional[float] = None
    annual_retirement_spending: Optional[float] = None

@dataclass
class ScenarioAssumptionUpdate:
    """Data transfer object for updating scenario assumptions."""
    retirement_age_1: Optional[int] = None
    retirement_age_2: Optional[int] = None
    default_growth_rate: Optional[float] = None
    inflation_rate: Optional[float] = None
    annual_retirement_spending: Optional[float] = None

def create_scenario(db: Session, scenario_data: ScenarioCreate) -> Scenario:
    """Create a new scenario for a plan."""
    db_scenario = Scenario(**vars(scenario_data))
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def get_scenario(db: Session, scenario_id: int) -> Optional[Scenario]:
    """Get a specific scenario by ID."""
    stmt = select(Scenario).where(Scenario.scenario_id == scenario_id)
    return db.scalar(stmt)

def get_plan_scenarios(
    db: Session, 
    plan_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Scenario]:
    """Get all scenarios for a specific plan."""
    stmt = select(Scenario).where(Scenario.plan_id == plan_id)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).unique())

def update_scenario(
    db: Session, 
    scenario_id: int, 
    scenario_data: ScenarioUpdate
) -> Optional[Scenario]:
    """Update a scenario's details."""
    stmt = select(Scenario).where(Scenario.scenario_id == scenario_id)
    db_scenario = db.scalar(stmt)
    if not db_scenario:
        return None
    
    update_data = {k: v for k, v in vars(scenario_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_scenario, key, value)
    
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def delete_scenario(db: Session, scenario_id: int) -> bool:
    """Delete a scenario."""
    stmt = select(Scenario).where(Scenario.scenario_id == scenario_id)
    db_scenario = db.scalar(stmt)
    if not db_scenario:
        return False
    
    db.delete(db_scenario)
    db.commit()
    return True

def create_scenario_assumptions(
    db: Session, 
    assumptions_data: ScenarioAssumptionCreate
) -> ScenarioAssumption:
    """Create assumptions for a scenario."""
    db_assumptions = ScenarioAssumption(**vars(assumptions_data))
    db.add(db_assumptions)
    db.commit()
    db.refresh(db_assumptions)
    return db_assumptions

def get_scenario_assumptions(
    db: Session, 
    scenario_id: int
) -> Optional[ScenarioAssumption]:
    """Get assumptions for a specific scenario."""
    stmt = select(ScenarioAssumption).where(ScenarioAssumption.scenario_id == scenario_id)
    return db.scalar(stmt)

def update_scenario_assumptions(
    db: Session,
    scenario_id: int,
    assumptions_data: ScenarioAssumptionUpdate
) -> Optional[ScenarioAssumption]:
    """Update a scenario's assumptions."""
    stmt = select(ScenarioAssumption).where(ScenarioAssumption.scenario_id == scenario_id)
    db_assumptions = db.scalar(stmt)
    if not db_assumptions:
        return None
    
    update_data = {k: v for k, v in vars(assumptions_data).items() if v is not None}
    for key, value in update_data.items():
        setattr(db_assumptions, key, value)
    
    db.commit()
    db.refresh(db_assumptions)
    return db_assumptions 