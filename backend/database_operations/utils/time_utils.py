def get_start_year_from_dob(dob: date, plan_creation_year: int) -> int:
    """Returns the start year for projections based on DOB and when plan was created."""

def get_age_at_year(dob: date, target_year: int) -> int:
    """Returns the age a person will be in a specific year."""

def get_year_for_age(dob: date, target_age: int) -> int:
    """Returns the year when a person will reach a specific age."""

def create_age_year_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping ages to years for the projection period."""

def create_year_age_mapping(dob: date, start_year: int, end_year: int) -> Dict[int, int]:
    """Creates a dictionary mapping years to ages for the projection period."""

def get_retirement_year(dob: date, retirement_age: int) -> int:
    """Returns the year when retirement begins based on DOB and retirement age."""

def get_final_projection_year(dob: date, final_age: int) -> int:
    """Returns the final year of projections based on DOB and final age."""