# tests/test_timeline_validations.py
from datetime import date
import pytest
from database_operations.validation.scenario_timeline_validation import validate_projection_timeline
from database_operations.utils.time_utils import get_age_in_year, get_year_for_age

def test_projection_timeline_validation():
    """Test validation of basic timeline constraints."""
    start_year = 2025
    
    # Valid timeline
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=2035,
        end_year=2045
    )
    
    # Invalid: retirement before start
    assert not validate_projection_timeline(
        start_year=start_year,
        retirement_year=2024,
        end_year=2045
    )
    
    # Invalid: end before retirement
    assert not validate_projection_timeline(
        start_year=start_year,
        retirement_year=2035,
        end_year=2034
    )

def test_age_based_timeline_consistency():
    """Test timeline consistency with age-based calculations."""
    dob = date(1970, 1, 1)
    start_year = 2025
    
    # Get retirement year from age
    retirement_age = 65
    retirement_year = get_year_for_age(dob, retirement_age)
    
    # Get end year from age
    final_age = 95
    end_year = get_year_for_age(dob, final_age)
    
    # Validate complete timeline
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=end_year
    )
    
    # Verify age calculations
    assert get_age_in_year(dob, retirement_year) == retirement_age
    assert get_age_in_year(dob, end_year) == final_age