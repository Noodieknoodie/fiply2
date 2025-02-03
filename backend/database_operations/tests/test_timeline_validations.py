# tests/test_timeline_validations.py
from datetime import date, timedelta
import pytest
from database_operations.validation.scenario_timeline_validation import validate_projection_timeline
from database_operations.utils.time_utils import (
    get_age_in_year, 
    get_year_for_age,
    validate_year_not_before_plan_creation,
    map_age_to_years
)

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

def test_partial_year_transitions():
    """Test timeline validation with partial year transitions."""
    # Test mid-year retirement transitions
    dob = date(1970, 6, 15)  # Mid-year birthday
    start_year = 2025
    retirement_age = 65
    
    # Calculate exact retirement date
    retirement_year = get_year_for_age(dob, retirement_age)
    
    # Verify retirement year calculation accounts for mid-year birthday
    assert get_age_in_year(dob, retirement_year) == retirement_age
    
    # Test retirement year validation
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=retirement_year + 10
    )
    
    # Test with different birth months
    early_year_dob = date(1970, 1, 1)
    late_year_dob = date(1970, 12, 31)
    
    early_retirement_year = get_year_for_age(early_year_dob, retirement_age)
    late_retirement_year = get_year_for_age(late_year_dob, retirement_age)
    
    # Verify age calculations for different birth months
    assert get_age_in_year(early_year_dob, early_retirement_year) == retirement_age
    assert get_age_in_year(late_year_dob, late_retirement_year) == retirement_age

def test_age_based_timeline_edge_cases():
    """Test timeline validation for age-based edge cases."""
    dob = date(1970, 1, 1)
    start_year = 2025
    
    # Test retirement at exact year boundary
    retirement_age = 65
    retirement_year = get_year_for_age(dob, retirement_age)
    
    # Verify timeline with exact boundary retirement
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=retirement_year + 30
    )
    
    # Test maximum age scenarios
    max_age = 120
    end_year = get_year_for_age(dob, max_age)
    
    # Verify timeline with maximum age
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=end_year
    )
    
    # Test century boundary transition
    century_boundary_dob = date(1999, 12, 31)
    century_retirement_age = 65
    century_retirement_year = get_year_for_age(century_boundary_dob, century_retirement_age)
    
    assert validate_projection_timeline(
        start_year=2025,
        retirement_year=century_retirement_year,
        end_year=century_retirement_year + 30
    )

def test_timeline_modification_validation():
    """Test validation of timeline modifications."""
    dob = date(1970, 1, 1)
    start_year = 2025
    original_retirement_age = 65
    original_retirement_year = get_year_for_age(dob, original_retirement_age)
    
    # Test moving retirement earlier
    early_retirement_age = 62
    early_retirement_year = get_year_for_age(dob, early_retirement_age)
    
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=early_retirement_year,
        end_year=original_retirement_year + 30
    )
    
    # Test moving retirement later
    late_retirement_age = 70
    late_retirement_year = get_year_for_age(dob, late_retirement_age)
    
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=late_retirement_year,
        end_year=late_retirement_year + 25
    )
    
    # Test extending end date
    extended_end_year = late_retirement_year + 35
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=late_retirement_year,
        end_year=extended_end_year
    )

def test_age_year_mapping_validation():
    """Test validation of age-to-year mapping scenarios."""
    dob = date(1970, 1, 1)
    start_year = 2025
    end_year = 2055
    
    # Generate complete age-to-year mapping
    age_year_map = map_age_to_years(dob, start_year, end_year)
    
    # Verify all ages are present
    start_age = get_age_in_year(dob, start_year)
    end_age = get_age_in_year(dob, end_year)
    
    assert len(age_year_map) == (end_age - start_age + 1)
    assert all(age in age_year_map for age in range(start_age, end_age + 1))
    
    # Verify correct year mapping
    for age, year in age_year_map.items():
        assert get_age_in_year(dob, year) == age

def test_invalid_timeline_scenarios():
    """Test various invalid timeline scenarios."""
    start_year = 2025
    
    # Test invalid year order
    with pytest.raises(ValueError):
        validate_projection_timeline(
            start_year=2030,  # Start after retirement
            retirement_year=2025,
            end_year=2045
        )
    
    # Test same year retirement
    with pytest.raises(ValueError):
        validate_projection_timeline(
            start_year=2025,
            retirement_year=2025,  # Same as start
            end_year=2045
        )
    
    # Test same year end
    with pytest.raises(ValueError):
        validate_projection_timeline(
            start_year=2025,
            retirement_year=2035,
            end_year=2035  # Same as retirement
        )

def test_timeline_consistency_across_scenarios():
    """Test timeline consistency when used across multiple scenarios."""
    dob = date(1970, 1, 1)
    start_year = 2025
    retirement_age = 65
    retirement_year = get_year_for_age(dob, retirement_age)
    end_year = retirement_year + 30
    
    # Base timeline
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=end_year
    )
    
    # Scenario variations
    variations = [
        (retirement_age - 3, 30),  # Early retirement
        (retirement_age + 3, 27),  # Late retirement
        (retirement_age, 35),      # Extended end date
        (retirement_age, 25)       # Shorter end date
    ]
    
    for var_retirement_age, years_after_retirement in variations:
        var_retirement_year = get_year_for_age(dob, var_retirement_age)
        var_end_year = var_retirement_year + years_after_retirement
        
        assert validate_projection_timeline(
            start_year=start_year,
            retirement_year=var_retirement_year,
            end_year=var_end_year
        )

def test_leap_year_handling():
    """Test timeline validation with leap year considerations."""
    # Test DOB on Feb 29
    leap_year_dob = date(1972, 2, 29)  # Leap year
    start_year = 2025
    retirement_age = 65
    
    retirement_year = get_year_for_age(leap_year_dob, retirement_age)
    
    # Verify correct age calculation for leap year birth date
    assert get_age_in_year(leap_year_dob, retirement_year) == retirement_age
    
    # Verify timeline validation works correctly with leap year DOB
    assert validate_projection_timeline(
        start_year=start_year,
        retirement_year=retirement_year,
        end_year=retirement_year + 30
    )