“””
## Retirement Income
- Start year, end year
- Amount
- Optional inflation toggle
- Input in absolute years (derived dynamically from selected person's retirement age)
- For SS/Pension/Deferred Comp, etc.
- Separate from scheduled inflows

## Time Handling Principles
- DOB is the only true date input
- All calculations reference absolute years internally
- Conversion rules:
  - Years ↔ Age: Derived dynamically from DOB when needed
  - Store values as entered and convert as needed

## Value Display Principles
- Inflation adjustments compound annually
- No partial year or day counting
- All events assumed to occur at year boundaries

1. Proper age-based activation of income streams
2. Support for lifetime income (no end age)
3. Optional inflation adjustments
4. Clear separation from scheduled inflows
5. Proper handling of DOB for age calculations
6. Utilities for analyzing income streams by type
“””

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date

from ..models import RetirementIncomePlan
from ..utils.money_utils import to_decimal, apply_annual_inflation
from ..utils.time_utils import (
    get_age_at_year,
    get_year_for_age
)

@dataclass
class RetirementIncomeFact:
    """Represents retirement income stream with all parameters."""
    income_id: int
    name: str
    owner: str
    annual_income: Decimal
    start_age: int
    end_age: Optional[int]
    include_in_nest_egg: bool
    apply_inflation: bool
    dob: date  # Date of birth of income owner for age calculations

@dataclass
class IncomeCalculationResult:
    """Results container tracking adjusted income amounts."""
    income_id: int
    income_name: str
    base_amount: Decimal
    adjusted_amount: Decimal
    inflation_adjustment: Decimal
    is_active: bool
    included_in_nest_egg: bool
    metadata: Dict

class RetirementIncomeCalculator:
    """Handles retirement income calculations with age-based timing."""
    
    def calculate_income_amount(
        self,
        income: RetirementIncomeFact,
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> IncomeCalculationResult:
        """
        Calculates retirement income for a specific year.
        
        Args:
            income: Income stream data container
            year: Year to calculate for
            inflation_rate: Annual inflation rate
            plan_start_year: Year plan started (for inflation calculations)
            
        Returns:
            Calculation results including base and adjusted amounts
        """
        # Determine if income is active based on age
        current_age = get_age_at_year(income.dob, year)
        is_active = self._is_income_active(income, current_age)
        
        if not is_active:
            return IncomeCalculationResult(
                income_id=income.income_id,
                income_name=income.name,
                base_amount=income.annual_income,
                adjusted_amount=Decimal('0'),
                inflation_adjustment=Decimal('0'),
                is_active=False,
                included_in_nest_egg=income.include_in_nest_egg,
                metadata=self._generate_calculation_metadata(
                    income, year, current_age, Decimal('0')
                )
            )
        
        # Start with base amount
        base_amount = income.annual_income
        adjusted_amount = base_amount
        inflation_adjustment = Decimal('0')
        
        # Apply inflation if enabled
        if income.apply_inflation:
            years_from_start = year - plan_start_year
            adjusted_amount = apply_annual_inflation(
                base_amount,
                inflation_rate,
                years_from_start
            )
            inflation_adjustment = adjusted_amount - base_amount
            
        return IncomeCalculationResult(
            income_id=income.income_id,
            income_name=income.name,
            base_amount=base_amount,
            adjusted_amount=adjusted_amount,
            inflation_adjustment=inflation_adjustment,
            is_active=True,
            included_in_nest_egg=income.include_in_nest_egg,
            metadata=self._generate_calculation_metadata(
                income, year, current_age, inflation_adjustment
            )
        )

    def calculate_multiple_income_streams(
        self,
        income_streams: List[RetirementIncomeFact],
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> List[IncomeCalculationResult]:
        """
        Calculates amounts for multiple income streams.
        
        Args:
            income_streams: List of income streams to calculate
            year: Year to calculate for
            inflation_rate: Annual inflation rate
            plan_start_year: Year plan started
            
        Returns:
            List of calculation results for each income stream
        """
        return [
            self.calculate_income_amount(
                income, year, inflation_rate, plan_start_year
            )
            for income in income_streams
        ]

    def aggregate_by_source(
        self,
        results: List[IncomeCalculationResult]
    ) -> Dict[str, Decimal]:
        """
        Groups and totals income by source name.
        
        Args:
            results: List of income calculation results
            
        Returns:
            Dictionary mapping source name to total income
        """
        totals = {}
        for result in results:
            if result.is_active:  # Only include active income
                source = result.income_name
                if source not in totals:
                    totals[source] = Decimal('0')
                totals[source] += result.adjusted_amount
        return totals

    def calculate_total_income(
        self,
        results: List[IncomeCalculationResult],
        nest_egg_only: bool = False
    ) -> Decimal:
        """
        Calculates total retirement income.
        
        Args:
            results: List of income calculation results
            nest_egg_only: If True, only sum income included in nest egg
            
        Returns:
            Total retirement income
        """
        return sum(
            r.adjusted_amount
            for r in results
            if r.is_active and (not nest_egg_only or r.included_in_nest_egg)
        )

    def calculate_total_inflation_impact(
        self,
        results: List[IncomeCalculationResult]
    ) -> Decimal:
        """
        Calculates total impact of inflation adjustments.
        
        Args:
            results: List of income calculation results
            
        Returns:
            Total amount added by inflation
        """
        return sum(
            r.inflation_adjustment
            for r in results
            if r.is_active
        )

    def _is_income_active(
        self,
        income: RetirementIncomeFact,
        current_age: int
    ) -> bool:
        """Determines if income is active based on current age."""
        if current_age < income.start_age:
            return False
            
        if income.end_age is not None and current_age > income.end_age:
            return False
            
        return True

    def _generate_calculation_metadata(
        self,
        income: RetirementIncomeFact,
        year: int,
        current_age: int,
        inflation_adjustment: Decimal
    ) -> Dict:
        """Creates metadata about calculation process."""
        return {
            'income_name': income.name,
            'owner': income.owner,
            'year': year,
            'current_age': current_age,
            'inflation_enabled': income.apply_inflation,
            'inflation_adjustment': str(inflation_adjustment),
            'start_age': income.start_age,
            'end_age': income.end_age or 'Lifetime',
            'is_lifetime_income': income.end_age is None
        }

    def validate_retirement_income_facts(
        self,
        income_streams: List[RetirementIncomeFact]
    ) -> None:
        """Validates income stream inputs before calculations."""
        for income in income_streams:
            # Validate amount is positive
            if income.annual_income <= 0:
                raise ValueError(
                    f"Income stream {income.income_id} has invalid amount"
                )
            
            # Validate age sequence
            if income.end_age is not None:
                if income.start_age > income.end_age:
                    raise ValueError(
                        f"Income stream {income.income_id} has invalid age sequence"
                    )

    def get_lifetime_income_streams(
        self,
        results: List[IncomeCalculationResult]
    ) -> List[IncomeCalculationResult]:
        """
        Returns list of income streams with no end age (lifetime).
        
        Args:
            results: List of income calculation results
            
        Returns:
            Filtered list of lifetime income streams
        """
        return [
            r for r in results 
            if 'is_lifetime_income' in r.metadata 
            and r.metadata['is_lifetime_income']
        ]

    def get_fixed_term_income_streams(
        self,
        results: List[IncomeCalculationResult]
    ) -> List[IncomeCalculationResult]:
        """
        Returns list of income streams with specific end ages.
        
        Args:
            results: List of income calculation results
            
        Returns:
            Filtered list of fixed-term income streams
        """
        return [
            r for r in results 
            if 'is_lifetime_income' in r.metadata 
            and not r.metadata['is_lifetime_income']
        ]
