"""Test fixtures for date utility functions."""

from datetime import date


# Basic date samples covering edge cases
SAMPLE_DATES = {
    "standard": date(1980, 6, 15),        # Mid-year date
    "leap_year": date(1960, 2, 29),       # Leap year date
    "year_end": date(1975, 12, 31),       # End of year
    "year_start": date(1970, 1, 1),       # Start of year
    "month_end": date(1980, 4, 30),       # End of month
    "month_start": date(1980, 5, 1)       # Start of month
}

# Sample households for testing different scenarios
SAMPLE_HOUSEHOLDS = [
    {
        "person1_dob": date(1960, 6, 15),     # Single person
        "person2_dob": None
    },
    {
        "person1_dob": date(1960, 6, 15),     # Couple, same year
        "person2_dob": date(1960, 8, 20)
    },
    {
        "person1_dob": date(1960, 6, 15),     # Couple, different years
        "person2_dob": date(1965, 8, 20)
    },
    {
        "person1_dob": date(1960, 2, 29),     # Leap year DOB
        "person2_dob": date(1965, 8, 20)
    }
]

# Sample periods for prorated calculations
SAMPLE_PERIODS = [
    {
        "start": date(2024, 1, 1),
        "end": date(2024, 12, 31),        # Full year
        "amount": 12000.00
    },
    {
        "start": date(2024, 6, 15),
        "end": date(2024, 12, 31),        # Partial year
        "amount": 12000.00
    },
    {
        "start": date(2024, 1, 1),
        "end": date(2025, 6, 30),         # Multi-year
        "amount": 12000.00
    },
    {
        "start": date(2024, 1, 1),
        "end": None,                       # Open-ended
        "amount": 12000.00
    }
]

# Sample planning horizons
SAMPLE_PLANNING_HORIZONS = [
    {
        "dob_1": date(1960, 6, 15),
        "dob_2": date(1965, 8, 20),
        "final_age_1": 95,
        "final_age_2": 90,
        "final_age_selector": 1            # Use person 1's age
    },
    {
        "dob_1": date(1960, 6, 15),
        "dob_2": None,                     # Single person
        "final_age_1": 95,
        "final_age_2": None,
        "final_age_selector": 1
    },
    {
        "dob_1": date(1960, 6, 15),
        "dob_2": date(1965, 8, 20),
        "final_age_1": 95,
        "final_age_2": 90,
        "final_age_selector": 2            # Use person 2's age
    }
]

# Sample age ranges for testing is_between_ages
SAMPLE_AGE_RANGES = [
    {
        "dob": date(1960, 6, 15),
        "check_date": date(2022, 1, 1),    # Changed to make person 61.5 years old
        "start_age": 62,
        "end_age": 70                      # Retirement window - should be FALSE as they're not 62 yet
    },
    {
        "dob": date(1960, 6, 15),
        "check_date": date(2030, 1, 1),
        "start_age": 65,
        "end_age": None                    # Open-ended period
    },
    {
        "dob": date(1960, 2, 29),         # Leap year DOB
        "check_date": date(2025, 3, 1),
        "start_age": 62,
        "end_age": 70
    }
]

# Expected results for age calculations
EXPECTED_AGES = {
    "current_age": {
        date(1960, 6, 15): 63,            # As of 2024
        date(1965, 8, 20): 58,
        date(1960, 2, 29): 63
    },
    "age_at_date": {
        (date(1960, 6, 15), date(2025, 6, 15)): 65,  # On 65th birthday
        (date(1960, 6, 15), date(2025, 6, 14)): 64,  # Day before birthday
        (date(1960, 2, 29), date(2024, 2, 29)): 64   # Leap year birthday
    }
} 