
# Supporting evidence from documentation:
# md
# ## Core Validations
# 1. Date of birth must be a valid past date.  
# 2. Retirement year must be after the start year.  
# 3. End year must be after retirement year.  
# 4. Start year must be before end year for inflows/outflows.  
# 5. Scenario overrides cannot create invalid timelines.  
# 6. Stepwise growth periods must be in chronological order and not overlap.

def validate_projection_timeline(start_year: int, retirement_year: int, end_year: int) -> bool:
    """Validates the core timeline follows: start_year < retirement_year < end_year."""

def validate_dob(dob: date) -> bool:
    """Validates DOB is a past date and within reasonable bounds."""

def validate_retirement_age(retirement_age: int) -> bool:
    """Validates retirement age is within reasonable bounds (e.g., 45-75)."""

def validate_final_age(final_age: int) -> bool:
    """Validates final age is within reasonable bounds (e.g., 70-100)."""

def is_within_projection_period(year: int, start_year: int, end_year: int) -> bool:
    """Checks if a given year falls within the projection period."""

def validate_stepwise_periods(periods: List[Tuple[int, int]]) -> bool:
    """Validates stepwise growth periods don't overlap and are in chronological order."""

def validate_age_sequence(start_age: int, retirement_age: int, final_age: int) -> bool:
    """Validates age progression follows: start_age < retirement_age < final_age."""