# backend/database_operations/validation/growth_validation.py
from typing import List, Dict, Any

def validate_stepwise_periods(periods: List[Dict[str, Any]], field_name: str) -> None:
    """Raises ValueError if periods overlap or are not in chronological order."""
    if not periods:
        return

    sorted_periods = sorted(periods, key=lambda x: x['start_year'])
    
    for i in range(len(sorted_periods) - 1):
        current, next_period = sorted_periods[i], sorted_periods[i + 1]

        if current.get('end_year') is None and i < len(sorted_periods) - 1:
            raise ValueError(f"{field_name} has an open-ended period that is not last")

        if current.get('end_year') is not None and current['end_year'] >= next_period['start_year']:
            raise ValueError(f"{field_name} contains overlapping periods")

def validate_growth_config_type(config_type: str, field_name: str) -> None:
    """Raises ValueError if config_type is not 'DEFAULT', 'OVERRIDE', or 'STEPWISE'."""
    if config_type not in {"DEFAULT", "OVERRIDE", "STEPWISE"}:
        raise ValueError(f"{field_name} must be 'DEFAULT', 'OVERRIDE', or 'STEPWISE'")
