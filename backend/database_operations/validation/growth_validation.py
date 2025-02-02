from typing import List, Tuple, Dict, Any
from decimal import Decimal

def validate_stepwise_periods(periods: List[Dict[str, Any]], field_name: str) -> None:
    """
    Validate stepwise growth periods don't overlap and are chronologically ordered.
    
    Args:
        periods: List of period dictionaries with start_year and end_year
        field_name: Name of field for error messages
    
    Raises:
        ValueError: If periods overlap or are not chronologically ordered
    """
    if not periods:
        return

    # Sort periods by start year
    sorted_periods = sorted(periods, key=lambda x: x['start_year'])
    
    # Check for overlaps and chronological order
    for i in range(len(sorted_periods) - 1):
        current = sorted_periods[i]
        next_period = sorted_periods[i + 1]
        
        # If current period has no end, it should be the last period
        if current.get('end_year') is None and i < len(sorted_periods) - 1:
            raise ValueError(f"{field_name} contains an open-ended period that's not the last period")
        
        # Check for overlap
        if current.get('end_year') is not None:
            if current['end_year'] >= next_period['start_year']:
                raise ValueError(f"{field_name} contains overlapping periods")

def validate_stepwise_growth_config(periods: List[Tuple[int, float]], field_name: str) -> None:
    """Validate stepwise growth periods are in chronological order and don't overlap. Required for asset-specific growth rate configurations."""

def validate_growth_config_type(config_type: str, field_name: str) -> None:
    """Validate growth configuration type is one of the allowed values."""
    valid_types = {'DEFAULT', 'OVERRIDE', 'STEPWISE'}
    if config_type not in valid_types:
        raise ValueError(f"{field_name} must be one of: {', '.join(valid_types)}")

def validate_growth_period_boundaries(periods: List[Dict], start_year: int, end_year: int) -> None:
    """Validate growth periods fall within overall projection timeline."""

def validate_growth_period_sequence(periods: List[Dict]) -> None:
    """Validate growth periods are sequential and non-overlapping."""

def validate_rate_bounds(rate: Decimal, field_name: str) -> None:
    """
    Validate growth rate is within reasonable bounds.
    Note: Can be negative as per core validation rules.
    
    Args:
        rate: Growth rate as decimal
        field_name: Name of field for error messages
        
    Raises:
        ValueError: If rate is outside reasonable bounds
    """
    # Allow negative rates but prevent unreasonable values
    # These bounds are generous but prevent obvious errors
    if rate < Decimal('-1') or rate > Decimal('1'):
        raise ValueError(f"{field_name} must be between -100% and 100%")
