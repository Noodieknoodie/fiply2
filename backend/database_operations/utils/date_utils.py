"""Date and age utility functions for financial planning calculations.

This module provides standardized age and year calculations for financial projections.
Following the principle of "store what you know, calculate what you need":
- Birth dates (DOB) are stored as full dates for accuracy
- Calculations are performed using ages and years for simplicity
- All financial events occur at the start of each year
- No partial year or month-based calculations

Key Principles:
- Ages increment at the start of each year
- A person turns 65 in the year they reach that age
- All calculations use whole years
- Financial events sequence: (1) Inflows (2) Inflation (3) Spending (4) Growth
"""

from datetime import date
from typing import List, Optional


def calculate_current_age(date_of_birth: date) -> int:
    """Calculate current age from date of birth.
    
    Used primarily for UI display and initial setup.
    For projections, use calculate_age_for_year instead.
    """
    return calculate_age_for_year(date_of_birth, date.today().year)


def calculate_age_for_year(date_of_birth: date, year: int) -> int:
    """Calculate person's age in a specific year.
    
    This is the core age calculation function for projections.
    Age is based on the year difference only, as all events
    occur at the start of each year.
    
    Args:
        date_of_birth: Person's date of birth
        year: The year to calculate age for
        
    Returns:
        Age the person will be/was in that year
    
    Example:
        >>> dob = date(1990, 6, 15)
        >>> calculate_age_for_year(dob, 2025)
        35
    """
    return year - date_of_birth.year


def get_current_year() -> int:
    """Get the current year for baseline calculations."""
    return date.today().year


def generate_projection_years(start_year: int, end_year: int) -> List[int]:
    """Generate sequence of years for projections.
    
    Args:
        start_year: First year of projection
        end_year: Last year of projection (inclusive)
        
    Returns:
        List of years from start to end
        
    Example:
        >>> generate_projection_years(2024, 2026)
        [2024, 2025, 2026]
    """
    return list(range(start_year, end_year + 1))


def is_retirement_age(current_age: int, retirement_age: int) -> bool:
    """Check if current age meets or exceeds retirement age.
    
    Simple comparison used for determining retirement status
    in a given projection year.
    
    Args:
        current_age: Age to check
        retirement_age: Age at which retirement begins
        
    Returns:
        True if person has reached retirement age
        
    Example:
        >>> is_retirement_age(65, 65)
        True
        >>> is_retirement_age(64, 65)
        False
    """
    return current_age >= retirement_age


def get_final_year(date_of_birth: date, final_age: int) -> int:
    """Calculate the year when a person reaches their final age.
    
    Used for determining projection end points.
    
    Args:
        date_of_birth: Person's date of birth
        final_age: Age to calculate final year for
        
    Returns:
        Year when person reaches final age
        
    Example:
        >>> dob = date(1990, 6, 15)
        >>> get_final_year(dob, 95)
        2085
    """
    return date_of_birth.year + final_age 