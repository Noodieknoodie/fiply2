"""Test helpers for base facts calculations."""

from datetime import date, timedelta
from typing import Dict, Optional
from ...calculations.base_facts import (
    GrowthConfig,
    GrowthType,
    TimeRange,
    OwnerType
)

def create_growth_config(
    rate: float,
    config_type: GrowthType = GrowthType.OVERRIDE,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> GrowthConfig:
    """Create a growth configuration for testing."""
    if start_date is None:
        start_date = date.today()
    
    return GrowthConfig(
        rate=rate,
        config_type=config_type,
        time_range=TimeRange(
            start_date=start_date,
            end_date=end_date
        )
    )

def create_stepwise_growth_configs(
    rates: Dict[str, float],
    start_date: Optional[date] = None
) -> list[GrowthConfig]:
    """Create a list of stepwise growth configurations for testing."""
    if start_date is None:
        start_date = date.today()
    
    configs = []
    current_date = start_date
    
    for period, rate in rates.items():
        if period == 'final':
            configs.append(create_growth_config(
                rate=rate,
                config_type=GrowthType.STEPWISE,
                start_date=current_date
            ))
        else:
            years = int(period.split('_')[0])
            end_date = current_date + timedelta(days=365 * years)
            
            configs.append(create_growth_config(
                rate=rate,
                config_type=GrowthType.STEPWISE,
                start_date=current_date,
                end_date=end_date
            ))
            current_date = end_date + timedelta(days=1)
    
    return configs 