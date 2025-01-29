"""Date and age utility functions for financial planning calculations.

This module provides standardized date/age calculations used throughout the application.
All functions use Python's dateutil library for consistent date arithmetic.

Key Principles:
- Ages are calculated using the financial industry standard (person turns 65 on their 65th birthday)
- Prorated amounts use a simple 365-day year for consistency
- Partial months are rounded to the start of month
"""

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Optional


def calculate_current_age(date_of_birth: date) -> int:
    """Calculate current age from date of birth."""
    today = date.today()
    return calculate_age_at_date(date_of_birth, today)


def calculate_age_at_date(date_of_birth: date, target_date: date) -> int:
    """Calculate age of a person at a specific date."""
    # Using relativedelta for accurate age calculation
    diff = relativedelta(target_date, date_of_birth)
    return diff.years


def get_date_for_age(date_of_birth: date, target_age: int) -> date:
    """Calculate the date when someone reaches a specific age."""
    return date_of_birth + relativedelta(years=target_age)


def is_between_ages(date_of_birth: date, check_date: date, start_age: int, end_age: Optional[int]) -> bool:
    """Determine if someone is between two ages at a specific date."""
    current_age = calculate_age_at_date(date_of_birth, check_date)
    
    if end_age is None:
        return current_age >= start_age
    
    return start_age <= current_age <= end_age


def get_planning_horizon_date(
    dob_1: date,
    dob_2: Optional[date],
    final_age_1: int,
    final_age_2: Optional[int],
    final_age_selector: int
) -> date:
    """Calculate the end date for projections based on selected person's final age."""
    if final_age_selector == 1:
        return get_date_for_age(dob_1, final_age_1)
    
    if dob_2 and final_age_2:
        return get_date_for_age(dob_2, final_age_2)
    
    # Fallback to person 1 if person 2's data is incomplete
    return get_date_for_age(dob_1, final_age_1)


def calculate_prorated_amount(annual_amount: float, start_date: date, end_date: Optional[date]) -> float:
    """Calculate prorated amount for partial years using simple 365-day year."""
    if end_date is None:
        return annual_amount
    
    # Calculate days in period
    days = (end_date - start_date).days + 1  # Include both start and end dates
    
    # Prorate based on 365-day year
    return (annual_amount * days) / 365


def is_date_range_active(check_date: date, start_date: date, end_date: Optional[date]) -> bool:
    """
    Determine if a date range is active at a specific date.
    
    A date range is considered active if:
    - The check_date is strictly after the start_date
    - AND either there is no end_date OR the check_date is on or before the end_date
    
    Args:
        check_date: The date to check
        start_date: The start date of the range
        end_date: The optional end date of the range
        
    Returns:
        bool: Whether the range is active at the check_date
    """
    return (
        start_date < check_date and
        (end_date is None or check_date <= end_date)
    ) 