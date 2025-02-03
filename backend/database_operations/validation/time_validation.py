from datetime import date

def validate_dob(dob: date) -> bool:
    """Returns True if dob is a past date."""
    return dob < date.today()

def validate_retirement_age(retirement_age: int) -> bool:
    """Returns True if retirement_age is positive."""
    return retirement_age > 0

def validate_final_age(final_age: int) -> bool:
    """Returns True if final_age is positive."""
    return final_age > 0

def validate_age_sequence(start_age: int, retirement_age: int, final_age: int) -> bool:
    """Returns True if start_age < retirement_age < final_age and all are positive."""
    return start_age > 0 and retirement_age > start_age and final_age > retirement_age

def is_within_projection_period(year: int, start_year: int, end_year: int) -> bool:
    """Returns True if year is within the projection range start_year to end_year (inclusive)."""
    return start_year <= year <= end_year if start_year <= end_year else False

def validate_year_not_before_plan_creation(year: int, plan_creation_year: int) -> bool:
    """Returns True if year is not before plan_creation_year."""
    return year >= plan_creation_year

def get_current_age(dob: date) -> int:
    """Returns the current age based on dob."""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def get_age_in_year(dob: date, year: int) -> int:
    """Returns age in a given year."""
    return year - dob.year - (1 if (year, 1, 1) <= (dob.year, dob.month, dob.day) else 0)

def get_year_for_age(dob: date, target_age: int) -> int:
    """Returns the year when a person reaches target_age."""
    return dob.year + target_age + ((dob.month, dob.day) > (1, 1))
