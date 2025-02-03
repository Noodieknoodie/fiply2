"""
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
""" 
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date

from ...utils.money_utils import to_decimal, apply_annual_inflation
from ...utils.time_utils import get_age_at_year


@dataclass
class RetirementIncomeFact:
    """Represents a retirement income stream."""
    income_id: int
    name: str
    owner: str
    annual_income: Decimal
    start_age: int
    end_age: Optional[int]
    include_in_nest_egg: bool
    apply_inflation: bool
    dob: date


@dataclass
class IncomeCalculationResult:
    """Stores results of income calculations."""
    income_id: int
    income_name: str
    base_amount: Decimal
    adjusted_amount: Decimal
    inflation_adjustment: Decimal
    is_active: bool
    included_in_nest_egg: bool
    metadata: Dict


class RetirementIncomeCalculator:
    """Handles retirement income calculations."""

    def calculate_income_amount(self, income: RetirementIncomeFact, year: int,
                                inflation_rate: Decimal, plan_start_year: int) -> IncomeCalculationResult:
        """Calculates income for a given year."""
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
                metadata=self._generate_metadata(income, year, current_age, Decimal('0'))
            )

        base_amount = income.annual_income
        inflation_adjustment = apply_annual_inflation(base_amount, inflation_rate, year - plan_start_year) - base_amount
        adjusted_amount = base_amount + inflation_adjustment if income.apply_inflation else base_amount

        return IncomeCalculationResult(
            income_id=income.income_id,
            income_name=income.name,
            base_amount=base_amount,
            adjusted_amount=adjusted_amount,
            inflation_adjustment=inflation_adjustment,
            is_active=True,
            included_in_nest_egg=income.include_in_nest_egg,
            metadata=self._generate_metadata(income, year, current_age, inflation_adjustment)
        )

    def calculate_multiple_income_streams(self, income_streams: List[RetirementIncomeFact], year: int,
                                          inflation_rate: Decimal, plan_start_year: int) -> List[IncomeCalculationResult]:
        """Calculates income for multiple streams."""
        return [self.calculate_income_amount(income, year, inflation_rate, plan_start_year) for income in income_streams]

    def aggregate_by_source(self, results: List[IncomeCalculationResult]) -> Dict[str, Decimal]:
        """Totals income by source."""
        totals = {}
        for result in results:
            if result.is_active:
                totals[result.income_name] = totals.get(result.income_name, Decimal('0')) + result.adjusted_amount
        return totals

    def calculate_total_income(self, results: List[IncomeCalculationResult], nest_egg_only: bool = False) -> Decimal:
        """Calculates total income."""
        return sum(r.adjusted_amount for r in results if r.is_active and (not nest_egg_only or r.included_in_nest_egg))

    def calculate_total_inflation_impact(self, results: List[IncomeCalculationResult]) -> Decimal:
        """Calculates total inflation impact."""
        return sum(r.inflation_adjustment for r in results if r.is_active)

    def _is_income_active(self, income: RetirementIncomeFact, current_age: int) -> bool:
        """Checks if income is active for the given age."""
        return income.start_age <= current_age <= (income.end_age or 100)

    def _generate_metadata(self, income: RetirementIncomeFact, year: int, current_age: int,
                           inflation_adjustment: Decimal) -> Dict:
        """Creates metadata for income calculations."""
        return {
            "income_name": income.name,
            "owner": income.owner,
            "year": year,
            "current_age": current_age,
            "inflation_enabled": income.apply_inflation,
            "inflation_adjustment": str(inflation_adjustment),
            "start_age": income.start_age,
            "end_age": income.end_age or "Lifetime",
            "is_lifetime_income": income.end_age is None
        }

    def validate_retirement_income_facts(self, income_streams: List[RetirementIncomeFact]) -> None:
        """Validates income streams before calculation."""
        for income in income_streams:
            if income.annual_income <= 0:
                raise ValueError(f"Income stream {income.income_id} has invalid amount")
            if income.end_age is not None and income.start_age > income.end_age:
                raise ValueError(f"Income stream {income.income_id} has invalid age sequence")

    def get_lifetime_income_streams(self, results: List[IncomeCalculationResult]) -> List[IncomeCalculationResult]:
        """Returns lifetime income streams."""
        return [r for r in results if r.metadata["is_lifetime_income"]]

    def get_fixed_term_income_streams(self, results: List[IncomeCalculationResult]) -> List[IncomeCalculationResult]:
        """Returns fixed-term income streams."""
        return [r for r in results if not r.metadata["is_lifetime_income"]]
