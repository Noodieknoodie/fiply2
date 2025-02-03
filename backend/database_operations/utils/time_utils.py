from datetime import date
from typing import Dict, Tuple

def get_start_year_from_dob(dob: date, plan_creation_year: int) -> int:
    """Returns the start year for projections (plan creation year)."""
    return plan_creation_year

def get_age_at_year(dob: date, target_year: int) -> int:
    """Returns age in a specific year, adjusting for birth date."""
    age = target_year - dob.year
    return age - 1 if (dob.month, dob.day) > (12, 31) else age

def get_year_for_age(dob: date, target_age: int) -> int:
    """Returns the year when a person reaches target_age."""
    return dob.year + target_age

def create_age_year_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Maps ages to years for a projection period."""
    return {get_age_at_year(dob, year): year for year in range(start_year, end_year + 1)}

def create_year_age_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Maps years to ages for a projection period."""
    return {year: get_age_at_year(dob, year) for year in range(start_year, end_year + 1)}

def get_retirement_year(dob: date, retirement_age: int) -> int:
    """Returns the year retirement begins."""
    return get_year_for_age(dob, retirement_age)

def get_final_projection_year(dob: date, final_age: int) -> int:
    """Returns the final year of projections."""
    return get_year_for_age(dob, final_age)

def get_projection_period(dob: date, plan_creation_year: int, final_age: int) -> Tuple[int, int]:
    """Returns (start_year, end_year) for the projection period."""
    return get_start_year_from_dob(dob, plan_creation_year), get_final_projection_year(dob, final_age)

def get_years_between(start_year: int, end_year: int) -> int:
    """Returns number of years between start_year and end_year, inclusive."""
    return max(0, end_year - start_year + 1)
