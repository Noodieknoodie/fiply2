"""Retirement income calculation module for base facts.

This module handles retirement income calculations using a year-based approach.
Following the principle of "store what you know, calculate what you need":
- Income sources are stored with start_age and optional end_age
- All calculations occur at the start of each year
- Inflation is applied before other adjustments
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, TypedDict, Literal
from enum import Enum

from ...utils.date_utils import calculate_age_for_year
from ...utils.money_utils import to_decimal, to_float, apply_annual_inflation
from . import OwnerType

@dataclass
class RetirementIncomeFact:
    """Represents a retirement income source with its core attributes.
    
    All monetary values are stored as float but converted to Decimal for calculations.
    Ages are stored as integers, representing the age at which income starts/ends.
    Birth dates are stored as ISO format strings (YYYY-MM-DD) but converted to date objects for calculations.
    """
    annual_income: float
    owner: OwnerType
    include_in_nest_egg: bool
    name: str
    start_age: int
    end_age: Optional[int]
    apply_inflation: bool
    person_dob: str  # ISO format date string 'YYYY-MM-DD'

    @classmethod
    def from_db_row(cls, row: Dict) -> 'RetirementIncomeFact':
        """Create a RetirementIncomeFact from a database row dictionary."""
        return cls(
            annual_income=float(row['annual_income']),
            owner=OwnerType(row['owner']),
            include_in_nest_egg=bool(row['include_in_nest_egg']),
            name=row['name'],
            start_age=int(row['start_age']),
            end_age=int(row['end_age']) if row.get('end_age') is not None else None,
            apply_inflation=bool(row['apply_inflation']),
            person_dob=row['person_dob'].isoformat() if hasattr(row['person_dob'], 'isoformat') else row['person_dob']
        )

class RetirementIncomeValueResult(TypedDict):
    """Type definition for retirement income calculation results."""
    name: str
    owner: str
    annual_amount: float
    adjusted_amount: float
    is_active: bool
    inflation_applied: bool
    included_in_totals: bool

def calculate_retirement_income_value(
    income: RetirementIncomeFact,
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> RetirementIncomeValueResult:
    """Calculate the value of a retirement income for a specific year.
    
    Following the SINGLE SOURCE OF TRUTH:
    1. Events apply at the start of the year
    2. Inflation applies at the start of the year
    3. Priority: (1) Inflows (2) Inflation (3) Spending (4) Growth
    
    Args:
        income: The retirement income to calculate
        calculation_year: The year to calculate the value for
        inflation_rate: Annual inflation rate for inflation-adjusted incomes
        base_year: Starting year for inflation calculations
        
    Returns:
        Dictionary containing the income details and calculated values
    """
    # Convert values to Decimal for precise calculations
    annual_amount = to_decimal(income.annual_income)
    
    # Convert string DOB to date object for age calculation
    year, month, day = map(int, income.person_dob.split('-'))
    dob = date(year, month, day)
    
    # Calculate age in the calculation year
    current_age = calculate_age_for_year(dob, calculation_year)
    
    # Check if income is active based on age
    is_active = (
        current_age >= income.start_age and
        (income.end_age is None or current_age <= income.end_age)
    )
    
    # Calculate the year this income starts (when person reaches start_age)
    start_year = year + income.start_age
    
    if not is_active:
        return {
            'name': income.name,
            'owner': income.owner.value,
            'annual_amount': to_float(annual_amount),
            'adjusted_amount': 0.0,
            'is_active': False,
            'inflation_applied': False,
            'included_in_totals': income.include_in_nest_egg
        }
    
    # Calculate inflation adjustment if applicable
    adjusted_amount = annual_amount
    inflation_applied = False
    
    if income.apply_inflation and inflation_rate > 0 and base_year is not None:
        # Only apply inflation if:
        # 1. We're past the base year
        # 2. This isn't the first year the income starts
        if calculation_year > base_year and calculation_year > start_year:
            # Apply inflation at the start of each year after base_year
            inflation_rate_decimal = to_decimal(str(inflation_rate))
            years_of_inflation = calculation_year - base_year
            for _ in range(years_of_inflation):
                adjusted_amount = apply_annual_inflation(adjusted_amount, inflation_rate_decimal)
            inflation_applied = True
    
    return {
        'name': income.name,
        'owner': income.owner.value,
        'annual_amount': to_float(annual_amount),
        'adjusted_amount': to_float(adjusted_amount),
        'is_active': True,
        'inflation_applied': inflation_applied,
        'included_in_totals': income.include_in_nest_egg
    }

def aggregate_retirement_income_by_owner(
    incomes: List[RetirementIncomeFact],
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> Dict[str, List[RetirementIncomeValueResult]]:
    """Group and calculate retirement incomes by owner for a specific year.
    
    Args:
        incomes: List of retirement incomes to aggregate
        calculation_year: Year to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted incomes
        base_year: Starting year for inflation calculations
        
    Returns:
        Dictionary mapping owner types to lists of calculated values
    """
    results: Dict[str, List[RetirementIncomeValueResult]] = {
        owner.value: [] for owner in OwnerType
    }
    
    for income in incomes:
        value = calculate_retirement_income_value(
            income,
            calculation_year,
            inflation_rate,
            base_year
        )
        results[income.owner.value].append(value)
    
    return results

class TotalRetirementIncomeResult(TypedDict):
    """Type definition for total retirement income calculation results."""
    total_income: float
    nest_egg_income: float
    metadata: Dict[str, Dict[Literal['total', 'active'], int]]

def calculate_total_retirement_income(
    incomes: List[RetirementIncomeFact],
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> TotalRetirementIncomeResult:
    """Calculate total retirement income values for a specific year.
    
    Args:
        incomes: List of retirement incomes to total
        calculation_year: Year to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted incomes
        base_year: Starting year for inflation calculations
        
    Returns:
        Dictionary containing total income, nest egg income, and metadata
    """
    aggregated = aggregate_retirement_income_by_owner(
        incomes,
        calculation_year,
        inflation_rate,
        base_year
    )
    
    # Initialize totals as Decimal
    total_income = to_decimal('0')
    nest_egg_income = to_decimal('0')
    total_count = 0
    active_count = 0
    
    # Add up totals across all owners
    for owner_incomes in aggregated.values():
        total_count += len(owner_incomes)
        active_count += sum(1 for income in owner_incomes if income['is_active'])
        
        for income in owner_incomes:
            amount = to_decimal(str(income['adjusted_amount']))
            total_income += amount
            
            # Only add to nest egg total if included and active
            if income['included_in_totals'] and income['is_active']:
                nest_egg_income += amount
    
    return {
        'total_income': to_float(total_income),
        'nest_egg_income': to_float(nest_egg_income),
        'metadata': {
            'incomes': {
                'total': total_count,
                'active': active_count
            }
        }
    } 