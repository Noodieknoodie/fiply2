"""Retirement income calculation module for base facts."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, TypedDict, Literal
from enum import Enum

from ...utils.date_utils import is_between_ages, calculate_age_at_date
from ...utils.money_utils import to_decimal, to_float
from . import OwnerType  # Add import for OwnerType

@dataclass
class RetirementIncomeFact:
    """Represents a retirement income source with its core attributes."""
    annual_income: float
    owner: OwnerType  # Updated to use OwnerType enum
    include_in_nest_egg: bool
    name: str
    start_age: int
    end_age: Optional[int]
    apply_inflation: bool
    person_dob: date

    @classmethod
    def from_db_row(cls, row: Dict) -> 'RetirementIncomeFact':
        """Create a RetirementIncomeFact from a database row dictionary."""
        return cls(
            annual_income=float(row['annual_income']),
            owner=OwnerType(row['owner']),  # Convert string to enum
            include_in_nest_egg=bool(row['include_in_nest_egg']),
            name=row['name'],
            start_age=int(row['start_age']),
            end_age=int(row['end_age']) if row.get('end_age') is not None else None,
            apply_inflation=bool(row['apply_inflation']),
            person_dob=row['person_dob']
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
    calculation_date: date,
    person_dob: date,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> RetirementIncomeValueResult:
    """
    Calculate the value of a retirement income at a specific date.
    
    A retirement income is considered active if:
    - The person's age at calculation_date is >= start_age
    - AND either there is no end_age OR the person's age at calculation_date is <= end_age
    
    Args:
        income: The retirement income to calculate
        calculation_date: The date to calculate the value for
        person_dob: Date of birth for the income owner
        inflation_rate: Annual inflation rate to apply if income is inflation-adjusted
        base_date: The starting date for calculations
        
    Returns:
        Dictionary containing the income details and calculated values
    """
    # Convert values to Decimal for precise calculations
    annual_amount = Decimal(str(income.annual_income))
    
    # Check if income is active at calculation date based on age
    is_active = is_between_ages(person_dob, calculation_date, income.start_age, income.end_age)
    
    if not is_active:
        return {
            'name': income.name,
            'owner': str(income.owner),
            'annual_amount': float(annual_amount.quantize(Decimal('0.01'))),
            'adjusted_amount': 0.0,
            'is_active': False,
            'inflation_applied': False,
            'included_in_totals': income.include_in_nest_egg
        }
    
    # Calculate inflation adjustment if applicable
    adjusted_amount = annual_amount
    inflation_applied = False
    
    if income.apply_inflation and inflation_rate > 0:
        years = Decimal(str((calculation_date - base_date).days)) / Decimal('365')
        inflation_factor = (Decimal('1') + Decimal(str(inflation_rate))) ** years
        adjusted_amount *= inflation_factor
        inflation_applied = True
    
    return {
        'name': income.name,
        'owner': str(income.owner),
        'annual_amount': float(annual_amount.quantize(Decimal('0.01'))),
        'adjusted_amount': float(adjusted_amount.quantize(Decimal('0.01'))),
        'is_active': True,
        'inflation_applied': inflation_applied,
        'included_in_totals': income.include_in_nest_egg
    }

def aggregate_retirement_income_by_owner(
    incomes: List[RetirementIncomeFact],
    calculation_date: date,
    person1_dob: date,
    person2_dob: Optional[date] = None,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> Dict[str, List[RetirementIncomeValueResult]]:
    """
    Group and calculate retirement incomes by owner.
    
    Args:
        incomes: List of retirement incomes to aggregate
        calculation_date: Date to calculate values for
        person1_dob: Date of birth for person 1
        person2_dob: Date of birth for person 2 (optional)
        inflation_rate: Annual inflation rate for inflation-adjusted incomes
        base_date: Starting date for calculations
        
    Returns:
        Dictionary mapping owners to lists of calculated values
    """
    results: Dict[str, List[RetirementIncomeValueResult]] = {}
    
    for income in incomes:
        # Determine which person's DOB to use
        dob = person1_dob if income.owner == 'person1' else person2_dob
        if dob is None:
            continue  # Skip if no DOB available for owner
            
        value = calculate_retirement_income_value(
            income,
            calculation_date,
            dob,
            inflation_rate,
            base_date
        )
        
        if income.owner not in results:
            results[income.owner] = []
        results[income.owner].append(value)
    
    return results

class TotalRetirementIncomeResult(TypedDict):
    """Type definition for total retirement income calculation results."""
    total_income: float
    nest_egg_income: float  # Added to match pattern in assets/liabilities
    metadata: Dict[str, Dict[Literal['total', 'active'], int]]

def calculate_total_retirement_income(
    incomes: List[RetirementIncomeFact],
    calculation_date: date,
    person1_dob: date,
    person2_dob: Optional[date] = None,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> TotalRetirementIncomeResult:
    """
    Calculate total retirement income values.
    
    Args:
        incomes: List of retirement incomes to total
        calculation_date: Date to calculate values for
        person1_dob: Date of birth for person 1
        person2_dob: Date of birth for person 2 (optional)
        inflation_rate: Annual inflation rate for inflation-adjusted incomes
        base_date: Starting date for calculations
        
    Returns:
        Dictionary containing total income, nest egg income, and metadata
    """
    aggregated = aggregate_retirement_income_by_owner(
        incomes,
        calculation_date,
        person1_dob,
        person2_dob,
        inflation_rate,
        base_date
    )
    
    # Initialize totals as Decimal
    total_income = Decimal('0')
    nest_egg_income = Decimal('0')
    total_count = 0
    active_count = 0
    
    # Add up totals across all owners
    for owner_incomes in aggregated.values():
        total_count += len(owner_incomes)
        active_count += sum(1 for income in owner_incomes if income['is_active'])
        
        for income in owner_incomes:
            amount = Decimal(str(income['adjusted_amount']))
            total_income += amount
            
            # Only add to nest egg total if included and active
            if income['included_in_totals'] and income['is_active']:
                nest_egg_income += amount
    
    return {
        'total_income': float(total_income.quantize(Decimal('0.01'))),
        'nest_egg_income': float(nest_egg_income.quantize(Decimal('0.01'))),
        'metadata': {
            'incomes': {
                'total': total_count,
                'active': active_count
            }
        }
    } 