"""Liability calculation module for base facts."""
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, TypedDict
from enum import Enum, auto
from ...utils.money_utils import to_decimal, to_float

class OwnerType(str, Enum):
    """Enum for liability ownership types."""
    PERSON_1 = "Person 1"
    PERSON_2 = "Person 2"
    JOINT = "Joint"

@dataclass
class LiabilityFact:
    """Represents a liability with its core attributes."""
    value: float
    owner: OwnerType
    include_in_nest_egg: bool
    category_id: int
    name: str
    interest_rate: Optional[float] = None

    @classmethod
    def from_db_row(cls, row: Dict) -> 'LiabilityFact':
        """Create a LiabilityFact from a database row dictionary."""
        return cls(
            value=float(row['value']),
            owner=OwnerType(row['owner']),
            include_in_nest_egg=bool(row['include_in_nest_egg']),
            category_id=int(row['liability_category_id']),
            name=row['liability_name'],
            interest_rate=float(row['interest_rate']) if row.get('interest_rate') is not None else None
        )

class LiabilityValueResult(TypedDict):
    """Type definition for liability value calculation results."""
    current_value: float
    projected_value: Optional[float]
    interest_rate: Optional[float]
    included_in_totals: bool

def calculate_liability_value(
    liability: LiabilityFact,
    calculation_date: date,
    base_date: date = date.today()
) -> LiabilityValueResult:
    """
    Calculate the current and projected value of a liability.
    
    Liabilities only grow if they have an interest rate - there is no default growth.
    - If no interest_rate: value stays exactly the same
    - If has interest_rate: compounds daily from base_date
    
    Args:
        liability: The liability to calculate values for
        calculation_date: The date to project the value to
        base_date: The starting date for calculations
        
    Returns:
        Dictionary containing current and projected values, applied interest rate,
        and whether the liability is included in total calculations
    """
    # Convert values to Decimal for precise calculations
    principal = to_decimal(liability.value)
    
    # If no interest rate, value stays exactly the same
    if liability.interest_rate is None:
        return {
            'current_value': to_float(principal),
            'projected_value': to_float(principal),  # Same as current
            'interest_rate': None,
            'included_in_totals': liability.include_in_nest_egg
        }
    
    # If before start date, no growth yet
    if calculation_date < base_date:
        return {
            'current_value': to_float(principal),
            'projected_value': to_float(principal),  # Same as current
            'interest_rate': liability.interest_rate,
            'included_in_totals': liability.include_in_nest_egg
        }
    
    # Has interest rate and at/after start date - apply compound interest
    rate = to_decimal(liability.interest_rate)
    
    # Calculate days of growth (minimum 1 day when dates match)
    days = max(to_decimal('1'), to_decimal((calculation_date - base_date).days))
    years = days / to_decimal('365')
    
    # Calculate compound interest using: P * (1 + r)^t
    projected_value = principal * (to_decimal('1') + rate) ** years
    
    return {
        'current_value': to_float(principal),
        'projected_value': to_float(projected_value),
        'interest_rate': liability.interest_rate,
        'included_in_totals': liability.include_in_nest_egg
    }

def aggregate_liabilities_by_category(
    liabilities: List[LiabilityFact],
    calculation_date: date,
    base_date: date = date.today()
) -> Dict[int, List[LiabilityValueResult]]:
    """
    Group liabilities by category and calculate their values.
    
    Args:
        liabilities: List of liabilities to aggregate
        calculation_date: Date to calculate values for
        base_date: Starting date for calculations
        
    Returns:
        Dictionary mapping category IDs to lists of calculated liability values
    """
    results: Dict[int, List[LiabilityValueResult]] = {}
    
    for liability in liabilities:
        if liability.category_id not in results:
            results[liability.category_id] = []
            
        value = calculate_liability_value(liability, calculation_date, base_date)
        results[liability.category_id].append(value)
    
    return results

class TotalLiabilitiesResult(TypedDict):
    """Type definition for total liabilities calculation results."""
    current_value: float
    projected_value: Optional[float]
    metadata: Dict[str, int]

def calculate_total_liabilities(
    liabilities: List[LiabilityFact],
    calculation_date: date,
    base_date: date = date.today()
) -> TotalLiabilitiesResult:
    """
    Calculate total liability values, considering only those included in nest egg calculations.
    
    Args:
        liabilities: List of liabilities to total
        calculation_date: Date to calculate values for
        base_date: Starting date for calculations
        
    Returns:
        Dictionary containing current and projected totals, plus metadata about the calculation
    """
    included_liabilities = [l for l in liabilities if l.include_in_nest_egg]
    all_values = [
        calculate_liability_value(l, calculation_date, base_date)
        for l in included_liabilities
    ]
    
    # Initialize totals as Decimal
    current_total = to_decimal('0')
    
    # Add up current values if there are any
    if all_values:
        current_total = sum(
            to_decimal(v['current_value'])
            for v in all_values
        )
    
    # Calculate projected total if any liabilities have interest
    projected_values = [
        to_decimal(v['projected_value'])
        for v in all_values
        if v['projected_value'] is not None
    ]
    projected_total = sum(projected_values) if projected_values else None
    
    # Add non-growing liabilities to projected total if it exists
    if projected_total is not None:
        non_growing = sum(
            to_decimal(v['current_value'])
            for v in all_values
            if v['projected_value'] is None
        )
        projected_total += non_growing
    
    return {
        'current_value': to_float(current_total),
        'projected_value': to_float(projected_total) if projected_total is not None else None,
        'metadata': {
            'liability_count': len(liabilities),
            'included_count': len(included_liabilities)
        }
    }
