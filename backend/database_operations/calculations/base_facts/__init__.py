# backend/database_operations/calculations/base_facts/__init__.py 

"""Base facts calculation module for financial planning.

This module provides core interfaces and utilities for calculating financial metrics
across different components (assets, liabilities, cash flows, etc.).
"""

from datetime import date
from typing import Optional, List, Dict, Union, TypedDict
from dataclasses import dataclass, field
from enum import Enum

class OwnerType(str, Enum):
    """Ownership types for financial components."""
    PERSON_1 = "Person 1"
    PERSON_2 = "Person 2"
    JOINT = "Joint"

class GrowthType(str, Enum):
    """Types of growth rate configurations."""
    DEFAULT = "DEFAULT"
    OVERRIDE = "OVERRIDE"
    STEPWISE = "STEPWISE"

@dataclass
class TimeRange:
    """Represents a time period for calculations."""
    start_date: date
    end_date: Optional[date] = None

@dataclass
class GrowthConfig:
    """Growth rate configuration for financial components."""
    rate: float
    config_type: GrowthType
    time_range: Optional[TimeRange] = None

@dataclass
class BaseFact:
    """Base class for financial facts."""
    value: float
    owner: OwnerType
    include_in_nest_egg: bool
    growth_config: Optional[GrowthConfig] = field(default=None)

class CalculationResult(TypedDict):
    """Standard format for calculation results."""
    current_value: float
    projected_value: Optional[float]
    growth_applied: Optional[float]
    included_in_totals: bool
    metadata: Dict[str, Union[str, float, bool]] 