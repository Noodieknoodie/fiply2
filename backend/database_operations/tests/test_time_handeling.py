# tests/test_time_handling.py
from datetime import date
import pytest
from database_operations.utils.time_utils import (
    get_age_in_year,
    get_year_for_age,
    validate_year_not_before_plan_creation
)

def test_age_year_conversion():
    """Test conversion between ages and years."""
    dob = date(1970, 1, 1)
    
    # Basic age calculation
    assert get_age_in_year(dob, 2025) == 55
    
    # Year for age calculation
    assert get_year_for_age(dob, 65) == 2035
    
    # Verify consistency
    retirement_age = 65
    retirement_year = get_year_for_age(dob, retirement_age)
    assert get_age_in_year(dob, retirement_year) == retirement_age

def test_plan_creation_year_validation():
    """Test validation of years against plan creation."""
    plan_creation_year = 2025
    
    # Valid years
    assert validate_year_not_before_plan_creation(2025, plan_creation_year)
    assert validate_year_not_before_plan_creation(2026, plan_creation_year)
    
    # Invalid years
    assert not validate_year_not_before_plan_creation(2024, plan_creation_year)

def test_age_calculations_with_partial_years():
    """Test age calculations considering month/day."""
    dob = date(1970, 6, 15)
    
    # Should be 54 at start of 2025
    assert get_age_in_year(dob, 2025) == 54
    
    # Different DOB timing
    early_dob = date(1970, 1, 1)
    late_dob = date(1970, 12, 31)
    
    assert get_age_in_year(early_dob, 2025) == 55
    assert get_age_in_year(late_dob, 2025) == 54