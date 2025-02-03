# backend/database_operations/utils/time_utils.py
from datetime import date
from typing import Dict, Tuple

# Handles computed values (age, years, mappings). No validation logic.


def get_start_year(plan_creation_year: int) -> int:
    """Returns the start year for projections (same as plan creation year)."""
    return plan_creation_year

def get_age_in_year(dob: date, year: int) -> int:
    """Returns age in a given year, adjusting for whether the birthday has passed."""
    return year - dob.year - (1 if (year, 1, 1) <= (dob.year, dob.month, dob.day) else 0)

def get_year_for_age(dob: date, target_age: int) -> int:
    """Returns the year when a person reaches a target age."""
    return dob.year + target_age

def map_age_to_years(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping ages to years."""
    return {get_age_in_year(dob, year): year for year in range(start_year, end_year + 1)}

def map_years_to_ages(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping years to ages."""
    return {year: get_age_in_year(dob, year) for year in range(start_year, end_year + 1)}

def get_retirement_year(dob: date, retirement_age: int) -> int:
    """Returns the year when retirement begins."""
    return get_year_for_age(dob, retirement_age)

def get_final_projection_year(dob: date, final_age: int) -> int:
    """Returns the last year of financial projections."""
    return get_year_for_age(dob, final_age)

def get_projection_period(dob: date, plan_creation_year: int, final_age: int) -> Tuple[int, int]:
    """Returns (start_year, end_year) for a projection."""
    return get_start_year(plan_creation_year), get_final_projection_year(dob, final_age)

def get_years_between(start_year: int, end_year: int) -> int:
    """Returns the number of years between two given years, inclusive."""
    return max(0, end_year - start_year + 1)
