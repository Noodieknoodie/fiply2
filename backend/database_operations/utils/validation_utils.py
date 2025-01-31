
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

def validate_positive_amount(amount: float, field_name: str) -> None:
    """Validate financial amounts are positive values. Required for: assets, liabilities, scheduled inflows, scheduled outflows, retirement income, and retirement spending."""

def validate_rate(rate: float, field_name: str) -> None:
    """Validate growth rate, inflation rate, or interest rate is numeric and within valid bounds. Can be negative as per core validation rules."""

def validate_stepwise_growth_config(periods: List[Tuple[int, float]], field_name: str) -> None:
    """Validate stepwise growth periods are in chronological order and don't overlap. Required for asset-specific growth rate configurations."""
"""
These were moved from the prior growth_validation.py file to this file.
"""
def validate_growth_config_type(config_type: str) -> None:
    """Validate growth configuration type is one of: DEFAULT, OVERRIDE, or STEPWISE."""

def validate_growth_period_boundaries(periods: List[Dict], start_year: int, end_year: int) -> None:
    """Validate growth periods fall within overall projection timeline."""

def validate_growth_period_sequence(periods: List[Dict]) -> None:
    """Validate growth periods are sequential and non-overlapping."""
