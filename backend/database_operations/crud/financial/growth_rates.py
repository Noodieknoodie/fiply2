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

from ...models import GrowthRateConfiguration 