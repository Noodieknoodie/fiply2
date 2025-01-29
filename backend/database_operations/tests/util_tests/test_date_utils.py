"""Tests for date utility functions."""

import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from ...utils.date_utils import (
    calculate_current_age,
    calculate_age_at_date,
    get_date_for_age,
    is_between_ages,
    get_planning_horizon_date,
    calculate_prorated_amount
)
from ..fixtures.date_test_data import (
    SAMPLE_DATES,
    SAMPLE_HOUSEHOLDS,
    SAMPLE_PERIODS,
    SAMPLE_PLANNING_HORIZONS,
    SAMPLE_AGE_RANGES,
    EXPECTED_AGES
)


def test_calculate_age_at_date():
    """Test age calculation at specific dates."""
    for (dob, target_date), expected_age in EXPECTED_AGES["age_at_date"].items():
        assert calculate_age_at_date(dob, target_date) == expected_age


def test_get_date_for_age():
    """Test getting date when someone reaches a specific age."""
    dob = SAMPLE_DATES["standard"]
    target_age = 65
    expected_date = date(2045, 6, 15)  # 1980-06-15 + 65 years
    assert get_date_for_age(dob, target_age) == expected_date


def test_is_between_ages():
    """Test age range checks."""
    for range_data in SAMPLE_AGE_RANGES:
        result = is_between_ages(
            range_data["dob"],
            range_data["check_date"],
            range_data["start_age"],
            range_data["end_age"]
        )
        # For this test, we'll verify specific cases
        if range_data["dob"] == date(1960, 6, 15):
            if range_data["check_date"] == date(2025, 1, 1):
                assert result == False  # Age 64.5, not in range 62-70
            elif range_data["check_date"] == date(2030, 1, 1):
                assert result == True  # Age 69.5, in range 65+


def test_get_planning_horizon_date():
    """Test planning horizon date calculations."""
    for horizon in SAMPLE_PLANNING_HORIZONS:
        result = get_planning_horizon_date(
            horizon["dob_1"],
            horizon["dob_2"],
            horizon["final_age_1"],
            horizon["final_age_2"],
            horizon["final_age_selector"]
        )
        
        # Calculate expected date based on selected person
        if horizon["final_age_selector"] == 1:
            expected = get_date_for_age(horizon["dob_1"], horizon["final_age_1"])
        else:
            expected = get_date_for_age(horizon["dob_2"], horizon["final_age_2"])
        
        assert result == expected


def test_calculate_prorated_amount():
    """Test prorated amount calculations."""
    for period in SAMPLE_PERIODS:
        result = calculate_prorated_amount(
            period["amount"],
            period["start"],
            period["end"]
        )
        
        if period["end"] is None:
            assert result == period["amount"]
        else:
            # Calculate expected amount based on days
            days = (period["end"] - period["start"]).days + 1
            expected = (period["amount"] * days) / 365
            assert abs(result - expected) < 0.01  # Allow small float difference


def test_leap_year_handling():
    """Test date calculations around leap years."""
    leap_dob = SAMPLE_DATES["leap_year"]
    
    # Test age calculation in leap year
    age_at_leap = calculate_age_at_date(leap_dob, date(2024, 2, 29))
    assert age_at_leap == 64
    
    # Test age calculation day after leap day
    age_after_leap = calculate_age_at_date(leap_dob, date(2024, 3, 1))
    assert age_after_leap == 64


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Test same date (age 0)
    dob = SAMPLE_DATES["standard"]
    assert calculate_age_at_date(dob, dob) == 0
    
    # Test day before birthday
    day_before = get_date_for_age(dob, 1) + relativedelta(days=-1)
    assert calculate_age_at_date(dob, day_before) == 0
    
    # Test exact birthday
    birthday = get_date_for_age(dob, 1)
    assert calculate_age_at_date(dob, birthday) == 1 