# ## Core Validations
# 1. Date of birth must be a valid past date.  
# 2. Retirement year must be after the start year.  
# 3. End year must be after retirement year.  
# 4. Start year must be before end year for inflows/outflows.  
# 5. Scenario overrides cannot create invalid timelines.  
# 6. Stepwise growth periods must be in chronological order and not overlap.


# backend/database_operations/validation/scenario_timeline_validation.py

from datetime import date
from typing import Dict, Optional, List
from ..models import InflowOutflow, GrowthRateConfiguration, RetirementIncomePlan
from ..utils.time_utils import get_year_for_age

def validate_projection_timeline(
    start_year: int,
    retirement_year: int, 
    end_year: int
) -> bool:
    if not all(isinstance(year, int) for year in [start_year, retirement_year, end_year]):
        return False
        
    return start_year < retirement_year < end_year

def validate_scenario_override_timeline(
    base_timeline: Dict[str, int],
    override_timeline: Dict[str, int]
) -> bool:
    start_year = override_timeline.get('start_year', base_timeline['start_year'])
    retirement_year = override_timeline.get('retirement_year', base_timeline['retirement_year'])
    end_year = override_timeline.get('end_year', base_timeline['end_year'])
    
    return validate_projection_timeline(start_year, retirement_year, end_year)

def validate_scenario_timeline_consistency(
    flows: List[InflowOutflow],
    growth_configs: List[GrowthRateConfiguration],
    income_plans: List[RetirementIncomePlan],
    start_year: int,
    retirement_year: int,
    end_year: int
) -> bool:
    if not validate_projection_timeline(start_year, retirement_year, end_year):
        return False
        
    try:
        for flow in flows:
            if flow.start_year < start_year:
                return False
            if flow.end_year and flow.end_year > end_year:
                return False

        for config in growth_configs:
            if config.start_year < start_year:
                return False
            if config.end_year and config.end_year > end_year:
                return False

        for income in income_plans:
            income_start = get_year_for_age(income.dob, income.start_age)
            if income_start < start_year:
                return False
            if income.end_age:
                income_end = get_year_for_age(income.dob, income.end_age)
                if income_end > end_year:
                    return False

        return True

    except Exception:
        return False