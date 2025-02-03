# backend/database_operations/validation/time_validation.py
from datetime import date

# time_validation.py: Strictly for validation checks. No computed values.


def validate_dob(dob: date) -> bool:
    """Returns True if dob is in the past."""
    return dob < date.today()

def validate_positive_age(age: int) -> bool:
    """Returns True if an age is a valid positive number."""
    return age > 0

def validate_age_sequence(start_age: int, retirement_age: int, final_age: int) -> bool:
    """Returns True if the sequence is logically valid: start_age < retirement_age < final_age."""
    return start_age > 0 and start_age < retirement_age < final_age

def validate_year_range(year: int, start_year: int, end_year: int) -> bool:
    """Returns True if a year is within the valid projection range."""
    return start_year <= year <= end_year if start_year <= end_year else False

def validate_year_not_before_plan_creation(year: int, plan_creation_year: int) -> bool:
    """Returns True if the given year is not before plan creation."""
    return year >= plan_creation_year

# In time_validation.py
def validate_timeline(start_year: int, retirement_year: int, end_year: int) -> None:
    if not (start_year < retirement_year < end_year):
        raise ValueError("Timeline must flow: start_year < retirement_year < end_year")