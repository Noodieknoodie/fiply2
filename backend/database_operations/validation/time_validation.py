from datetime import date, datetime
from typing import Optional

def validate_dob(dob: date) -> bool:
    """
    Validates DOB is a past date.
    
    Args:
        dob: Date of birth to validate
        
    Returns:
        True if valid, False otherwise
        
    Rules:
        - Must be a past date (impossible to plan for someone not born yet)
    """
    return dob < date.today()

def validate_retirement_age(retirement_age: int) -> bool:
    """
    Validates retirement age is possible.
    
    Args:
        retirement_age: Age at retirement
        
    Returns:
        True if valid, False otherwise
        
    Rules:
        - Must be > 0 (impossible to retire before being born)
    """
    return retirement_age > 0

def validate_final_age(final_age: int) -> bool:
    """
    Validates final age is possible.
    
    Args:
        final_age: Final age for planning
        
    Returns:
        True if valid, False otherwise
        
    Rules:
        - Must be > 0 (impossible to have negative age)
    """
    return final_age > 0

def validate_age_sequence(start_age: int, retirement_age: int, final_age: int) -> bool:
    """
    Validates age progression follows: start_age < retirement_age < final_age.
    
    Args:
        start_age: Current/starting age
        retirement_age: Age at retirement
        final_age: Final age for planning
        
    Returns:
        True if sequence is valid, False otherwise
        
    Rules:
        - Must be in strictly ascending order (impossible to retire before starting or die before retiring)
        - All ages must be > 0
    """
    # Validate individual ages are possible
    if not all(age > 0 for age in (start_age, retirement_age, final_age)):
        return False
        
    # Validate sequence (impossible to go backwards in time)
    return start_age < retirement_age < final_age

def is_within_projection_period(year: int, start_year: int, end_year: int) -> bool:
    """
    Checks if a given year falls within the projection period.
    
    Args:
        year: Year to check
        start_year: Beginning of projection period
        end_year: End of projection period
        
    Returns:
        True if year is within bounds, False otherwise
        
    Rules:
        - Year must be >= start_year (impossible to project before start)
        - Year must be <= end_year (impossible to project after end)
        - Start must be before end (impossible to go backwards)
    """
    # Validate sequence (impossible to go backwards)
    if start_year > end_year:
        return False
        
    # Check if year is within bounds
    return start_year <= year <= end_year

def validate_year_not_before_plan_creation(year: int, plan_creation_year: int) -> bool:
    """
    Validates that a year is not before the plan creation year.
    
    Args:
        year: Year to validate
        plan_creation_year: Year the plan was created
        
    Returns:
        True if valid, False otherwise
        
    Rules:
        - Year must be >= plan_creation_year (impossible to project before plan exists)
    """
    return year >= plan_creation_year

def get_current_age(dob: date) -> int:
    """
    Calculates current age from date of birth.
    
    Args:
        dob: Date of birth
        
    Returns:
        Current age in years
        
    Note:
        Handles leap years and partial years correctly
    """
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def get_age_in_year(dob: date, year: int) -> int:
    """
    Calculates age a person will be in a given year.
    
    Args:
        dob: Date of birth
        year: Target year
        
    Returns:
        Age in target year
        
    Note:
        Used for converting between absolute years and ages
    """
    return year - dob.year - (1 if (year, 1, 1) <= (dob.year, dob.month, dob.day) else 0)

def get_year_for_age(dob: date, target_age: int) -> int:
    """
    Calculates year when a person will reach a target age.
    
    Args:
        dob: Date of birth
        target_age: Age to calculate year for
        
    Returns:
        Year when person reaches target age
        
    Note:
        Used for converting between ages and absolute years
    """
    return dob.year + target_age + (1 if (dob.month, dob.day) > (1, 1) else 0)
