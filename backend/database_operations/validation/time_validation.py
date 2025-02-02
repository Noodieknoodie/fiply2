from datetime import date

def validate_dob(dob: date) -> bool:
    """Validates DOB is a past date and within reasonable bounds."""


def validate_retirement_age(retirement_age: int) -> bool:
    """Validates retirement age is within reasonable bounds (e.g., 45-75)."""

def validate_final_age(final_age: int) -> bool:
    """Validates final age is within reasonable bounds (e.g., 70-100)."""

def validate_age_sequence(start_age: int, retirement_age: int, final_age: int) -> bool:
    """Validates age progression follows: start_age < retirement_age < final_age."""

def is_within_projection_period(year: int, start_year: int, end_year: int) -> bool:
    """Checks if a given year falls within the projection period."""
