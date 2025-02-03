"""
Liability calculation module.
Unlike assets which use a complex growth rate system, liabilities use a simple interest model.
Key differences:
- No default growth rate usage
- Optional simple interest rate
- Fixed value if no rate specified
"""

from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ...utils.money_utils import to_decimal, apply_annual_compound_rate
from ...utils.time_utils import validate_year_not_before_plan_creation


@dataclass
class LiabilityFact:
    """Stores liability details for calculations."""
    liability_id: int
    value: Decimal
    interest_rate: Optional[Decimal]
    category_id: int
    include_in_nest_egg: bool
    plan_creation_year: Optional[int]


@dataclass
class LiabilityCalculationResult:
    """Stores liability calculation results."""
    liability_id: int
    starting_value: Decimal
    ending_value: Decimal
    interest_amount: Decimal
    category_id: int
    has_interest: bool
    metadata: Dict


class LiabilityCalculator:
    """Performs liability calculations using a simple interest model."""

    @staticmethod
    def calculate_liability_value(liability: LiabilityFact, year: int) -> LiabilityCalculationResult:
        """Computes liability value for a given year."""
        if liability.plan_creation_year:
            validate_year_not_before_plan_creation(year, liability.plan_creation_year)

        starting_value = liability.value
        ending_value, interest_amount = LiabilityCalculator.apply_interest(starting_value, liability.interest_rate)

        return LiabilityCalculationResult(
            liability_id=liability.liability_id,
            starting_value=starting_value,
            ending_value=ending_value,
            interest_amount=interest_amount,
            category_id=liability.category_id,
            has_interest=liability.interest_rate is not None,
            metadata=LiabilityCalculator.generate_metadata(liability, year, starting_value, ending_value)
        )

    @staticmethod
    def calculate_multiple_liabilities(liabilities: List[LiabilityFact], year: int) -> List[LiabilityCalculationResult]:
        """Computes liability values for multiple liabilities."""
        return [LiabilityCalculator.calculate_liability_value(liability, year) for liability in liabilities]

    @staticmethod
    def aggregate_by_category(results: List[LiabilityCalculationResult]) -> Dict[int, Decimal]:
        """Sums liabilities by category."""
        totals = {}
        for result in results:
            totals[result.category_id] = totals.get(result.category_id, Decimal('0')) + result.ending_value
        return totals

    @staticmethod
    def calculate_nest_egg_total(results: List[LiabilityCalculationResult]) -> Decimal:
        """Computes total liabilities marked as included in the nest egg."""
        return sum(result.ending_value for result in results if result.include_in_nest_egg)

    @staticmethod
    def apply_interest(value: Decimal, rate: Optional[Decimal]) -> Tuple[Decimal, Decimal]:
        """Applies simple interest for one period."""
        if rate is None:
            return value, Decimal('0')
        ending_value = apply_annual_compound_rate(value, rate)
        return ending_value, ending_value - value

    @staticmethod
    def calculate_weighted_average_rate(liabilities: List[Tuple[Decimal, Optional[Decimal]]]) -> Optional[Decimal]:
        """Computes weighted average interest rate across liabilities."""
        total_value = sum(value for value, rate in liabilities if rate)
        weighted_sum = sum(value * rate for value, rate in liabilities if rate)
        return weighted_sum / total_value if total_value else None

    @staticmethod
    def project_liability_value(current_value: Decimal, interest_rate: Optional[Decimal], years: int) -> Decimal:
        """Projects liability value over a number of years."""
        return apply_annual_compound_rate(current_value, interest_rate, years) if interest_rate else current_value

    @staticmethod
    def validate_liability_values(liabilities: List[Tuple[int, Decimal]]) -> None:
        """Ensures all liabilities have positive values."""
        for lid, value in liabilities:
            if value <= 0:
                raise ValueError(f"Liability {lid} has invalid value: {value}")

    @staticmethod
    def calculate_total_interest(results: List[Tuple[Decimal, Decimal]]) -> Decimal:
        """Computes total interest across all liabilities."""
        return sum(ending - starting for starting, ending in results)

    @staticmethod
    def identify_fixed_value_liabilities(liabilities: List[Tuple[int, Optional[Decimal]]]) -> List[int]:
        """Identifies liabilities with no interest rate."""
        return [lid for lid, rate in liabilities if rate is None]

    @staticmethod
    def identify_high_interest_liabilities(liabilities: List[Tuple[int, Optional[Decimal]]], threshold: Decimal) -> List[int]:
        """Identifies liabilities with interest rates exceeding a threshold."""
        return [lid for lid, rate in liabilities if rate and rate > threshold]

    @staticmethod
    def generate_metadata(liability: LiabilityFact, year: int, start_value: Decimal, end_value: Decimal) -> Dict:
        """Creates metadata for liability calculations."""
        return {
            "liability_id": liability.liability_id,
            "year": year,
            "starting_value": str(start_value),
            "ending_value": str(end_value),
            "interest_amount": str(end_value - start_value),
            "has_interest": liability.interest_rate is not None,
            "interest_rate": str(liability.interest_rate) if liability.interest_rate else None,
            "is_fixed_value": liability.interest_rate is None,
            "plan_creation_year": liability.plan_creation_year
        }
