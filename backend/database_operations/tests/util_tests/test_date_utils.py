"""Tests for date and age utility functions.

This test suite verifies the simplified year-based age calculations.
No partial years, no complex date arithmetic - just simple integer math.
"""

import pytest
from datetime import date
from ...utils.date_utils import (
    calculate_current_age,
    calculate_age_for_year,
    get_current_year,
    generate_projection_years,
    is_retirement_age,
    get_final_year
)

# Test Data
SAMPLE_DOB = date(1990, 6, 15)
CURRENT_YEAR = date.today().year


def test_calculate_current_age():
    """Test current age calculation."""
    # This will need to be updated each year
    expected_age = CURRENT_YEAR - SAMPLE_DOB.year
    assert calculate_current_age(SAMPLE_DOB) == expected_age


def test_calculate_age_for_year():
    """Test age calculation for specific years."""
    test_cases = [
        (SAMPLE_DOB, 2024, 34),  # Basic case
        (SAMPLE_DOB, 2025, 35),  # Next year
        (SAMPLE_DOB, 1990, 0),   # Birth year
        (SAMPLE_DOB, 1989, -1),  # Before birth
        (SAMPLE_DOB, 2090, 100), # Far future
    ]
    
    for dob, year, expected_age in test_cases:
        assert calculate_age_for_year(dob, year) == expected_age


def test_get_current_year():
    """Test current year matches system clock."""
    assert get_current_year() == date.today().year


def test_generate_projection_years():
    """Test year sequence generation."""
    test_cases = [
        (2024, 2026, [2024, 2025, 2026]),  # Normal case
        (2024, 2024, [2024]),              # Single year
        (2024, 2023, []),                  # Invalid range
    ]
    
    for start, end, expected in test_cases:
        assert generate_projection_years(start, end) == expected


def test_is_retirement_age():
    """Test retirement age comparison."""
    test_cases = [
        (65, 65, True),   # Exact retirement age
        (64, 65, False),  # One year before
        (66, 65, True),   # After retirement
        (0, 65, False),   # Far before
        (100, 65, True),  # Far after
    ]
    
    for current_age, retirement_age, expected in test_cases:
        assert is_retirement_age(current_age, retirement_age) == expected


def test_get_final_year():
    """Test final year calculation."""
    test_cases = [
        (SAMPLE_DOB, 95, 2085),   # Normal case
        (SAMPLE_DOB, 0, 1990),    # Birth year
        (SAMPLE_DOB, 100, 2090),  # Century
    ]
    
    for dob, final_age, expected_year in test_cases:
        assert get_final_year(dob, final_age) == expected_year 