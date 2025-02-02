# ## Core Validations
# 1. Date of birth must be a valid past date.  
# 2. Retirement year must be after the start year.  
# 3. End year must be after retirement year.  
# 4. Start year must be before end year for inflows/outflows.  
# 5. Scenario overrides cannot create invalid timelines.  
# 6. Stepwise growth periods must be in chronological order and not overlap.


from datetime import date
from typing import Dict

def validate_projection_timeline(start_year: int, retirement_year: int, end_year: int) -> bool:
    """Validates the core timeline follows: start_year < retirement_year < end_year."""


def validate_scenario_override_timeline(
    base_timeline: Dict[str, int], 
    override_timeline: Dict[str, int]
) -> bool:
    """Validates that scenario timeline overrides maintain valid sequence: start < retirement < end."""

def validate_scenario_timeline_consistency(
    scenario_id: int,
    start_year: int,
    retirement_year: int,
    end_year: int
) -> bool:
    """Validates all scenario components (cash flows, growth periods, etc.) fall within timeline bounds."""