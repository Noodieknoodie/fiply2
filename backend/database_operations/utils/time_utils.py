from datetime import date
from typing import Dict, Tuple

def get_start_year_from_dob(dob: date, plan_creation_year: int) -> int:
    """Returns the start year for projections based on DOB and when plan was created."""
    try:
        # Projections always begin in the year the plan was created
        return plan_creation_year
    except Exception as e:
        raise ValueError(f"Error determining start year from DOB {dob} and creation year {plan_creation_year}") from e

def get_age_at_year(dob: date, target_year: int) -> int:
    """Returns the age a person will be in a specific year."""
    try:
        # Calculate age based on year difference
        age = target_year - dob.year
        # Adjust if birthday hasn't occurred yet in target year
        if target_year > dob.year and (dob.month, dob.day) > (12, 31):
            age -= 1
        return age
    except Exception as e:
        raise ValueError(f"Error calculating age for DOB {dob} at year {target_year}") from e

def get_year_for_age(dob: date, target_age: int) -> int:
    """Returns the year when a person will reach a specific age."""
    try:
        return dob.year + target_age
    except Exception as e:
        raise ValueError(f"Error determining year for DOB {dob} at age {target_age}") from e

def create_age_year_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping ages to years for the projection period."""
    try:
        return {get_age_at_year(dob, year): year 
                for year in range(start_year, end_year + 1)}
    except Exception as e:
        raise ValueError(f"Error creating age-year mapping for period {start_year}-{end_year}") from e

def create_year_age_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping years to ages for the projection period."""
    try:
        return {year: get_age_at_year(dob, year) 
                for year in range(start_year, end_year + 1)}
    except Exception as e:
        raise ValueError(f"Error creating year-age mapping for period {start_year}-{end_year}") from e

def get_retirement_year(dob: date, retirement_age: int) -> int:
    """Returns the year when retirement begins based on DOB and retirement age."""
    try:
        return get_year_for_age(dob, retirement_age)
    except Exception as e:
        raise ValueError(f"Error calculating retirement year for DOB {dob} at age {retirement_age}") from e

def get_final_projection_year(dob: date, final_age: int) -> int:
    """Returns the final year of projections based on DOB and final age."""
    try:
        return get_year_for_age(dob, final_age)
    except Exception as e:
        raise ValueError(f"Error calculating final projection year for DOB {dob} at age {final_age}") from e

def get_projection_period(dob: date, plan_creation_year: int, final_age: int) -> Tuple[int, int]:
    """Returns the start and end years for the entire projection period.
    
    Args:
        dob: Date of birth
        plan_creation_year: Year when the plan was created
        final_age: Final age for projections
        
    Returns:
        Tuple of (start_year, end_year) defining the projection period
    """
    try:
        start_year = get_start_year_from_dob(dob, plan_creation_year)
        end_year = get_final_projection_year(dob, final_age)
        return (start_year, end_year)
    except Exception as e:
        raise ValueError(f"Error determining projection period for DOB {dob}, creation year {plan_creation_year}, final age {final_age}") from e

def get_years_between(start_year: int, end_year: int) -> int:
    """Calculate the number of years between two years, inclusive.
    
    Args:
        start_year: Beginning year
        end_year: Ending year
        
    Returns:
        Number of years between start_year and end_year, inclusive
    """
    try:
        # Add 1 to include both start and end years
        return max(0, end_year - start_year + 1)
    except Exception as e:
        raise ValueError(f"Error calculating years between {start_year} and {end_year}") from e