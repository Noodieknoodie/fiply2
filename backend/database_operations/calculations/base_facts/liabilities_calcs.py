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
from datetime import date

from ...utils.money_utils import to_decimal, apply_annual_compound_rate, round_to_currency

@dataclass
class LiabilityFact:
    """Container for liability calculation inputs."""
    liability_id: int
    value: Decimal
    interest_rate: Optional[Decimal]
    category_id: int
    include_in_nest_egg: bool

@dataclass
class LiabilityCalculationResult:
    """Container for liability calculation results."""
    liability_id: int
    starting_value: Decimal
    ending_value: Decimal
    interest_amount: Decimal
    category_id: int
    has_interest: bool
    metadata: Dict

class LiabilityCalculator:
    """
    Handles liability calculations with simple interest model.
    Combines original calculator functionality with helper methods.
    """
    
    @staticmethod
    def calculate_liability_value(
        liability: LiabilityFact,
        year: int
    ) -> LiabilityCalculationResult:
        """
        Calculate liability value for a single year period.
        
        Args:
            liability: Liability fact container
            year: Calculation year
            
        Returns:
            Calculation result with starting and ending values
        """
        starting_value = liability.value
        ending_value, interest_amount = LiabilityCalculator.apply_interest(
            starting_value,
            liability.interest_rate
        )
        
        metadata = LiabilityCalculator.generate_calculation_metadata(
            liability.liability_id,
            starting_value,
            ending_value,
            liability.interest_rate,
            year
        )
        
        return LiabilityCalculationResult(
            liability_id=liability.liability_id,
            starting_value=starting_value,
            ending_value=ending_value,
            interest_amount=interest_amount,
            category_id=liability.category_id,
            has_interest=liability.interest_rate is not None,
            metadata=metadata
        )

    @staticmethod
    def calculate_multiple_liabilities(
        liabilities: List[LiabilityFact],
        year: int
    ) -> List[LiabilityCalculationResult]:
        """
        Calculate values for multiple liabilities.
        
        Args:
            liabilities: List of liability facts
            year: Calculation year
            
        Returns:
            List of calculation results
        """
        return [
            LiabilityCalculator.calculate_liability_value(liability, year)
            for liability in liabilities
        ]

    @staticmethod
    def aggregate_by_category(
        results: List[LiabilityCalculationResult]
    ) -> Dict[int, Decimal]:
        """
        Aggregate liability values by category.
        
        Args:
            results: List of calculation results
            
        Returns:
            Dictionary mapping category IDs to total values
        """
        return LiabilityCalculator.calculate_category_totals([
            (result.liability_id, result.ending_value, result.category_id)
            for result in results
        ])

    @staticmethod
    def calculate_nest_egg_total(
        results: List[LiabilityCalculationResult]
    ) -> Decimal:
        """
        Calculate total for nest egg liabilities.
        
        Args:
            results: List of calculation results
            
        Returns:
            Total value of nest egg liabilities
        """
        return sum(
            result.ending_value
            for result in results
            if result.include_in_nest_egg
        )

    # Helper Methods (integrated from liabilities_helpers.py)
    
    @staticmethod
    def apply_interest(
        value: Decimal,
        rate: Optional[Decimal]
    ) -> Tuple[Decimal, Decimal]:
        """
        Applies simple interest for one year period.
        
        Args:
            value: Current liability value
            rate: Optional interest rate
            
        Returns:
            Tuple of (ending_value, interest_amount)
        """
        if rate is None:
            return value, Decimal('0')
        ending_value = apply_annual_compound_rate(value, rate)
        interest_amount = ending_value - value
        return ending_value, interest_amount

    @staticmethod
    def is_interest_applicable(
        interest_rate: Optional[Decimal],
        liability_id: int
    ) -> Tuple[bool, str]:
        """
        Determines if liability has valid interest rate configuration.
        
        Args:
            interest_rate: Optional interest rate
            liability_id: ID of liability
            
        Returns:
            Tuple of (is_applicable, reason)
        """
        if interest_rate is None:
            return False, "no_rate_specified"
        if interest_rate == 0:
            return False, "zero_rate"
        return True, "rate_applicable"

    @staticmethod
    def calculate_category_totals(
        results: List[Tuple[int, Decimal, int]]
    ) -> Dict[int, Decimal]:
        """
        Computes running totals by category.
        
        Args:
            results: List of (liability_id, value, category_id) tuples
            
        Returns:
            Dictionary mapping category IDs to total values
        """
        totals = {}
        for _, value, category_id in results:
            if category_id not in totals:
                totals[category_id] = Decimal('0')
            totals[category_id] += value
        return totals

    @staticmethod
    def generate_calculation_metadata(
        liability_id: int,
        starting_value: Decimal,
        ending_value: Decimal,
        interest_rate: Optional[Decimal],
        year: int
    ) -> Dict:
        """
        Creates metadata about liability calculation.
        
        Args:
            liability_id: ID of liability
            starting_value: Value at start of year
            ending_value: Value at end of year
            interest_rate: Optional interest rate
            year: Calculation year
            
        Returns:
            Dictionary containing calculation metadata
        """
        interest_amount = ending_value - starting_value
        return {
            'liability_id': liability_id,
            'year': year,
            'starting_value': str(starting_value),
            'ending_value': str(ending_value),
            'interest_amount': str(interest_amount),
            'has_interest': interest_rate is not None,
            'interest_rate': str(interest_rate) if interest_rate else None,
            'is_fixed_value': interest_rate is None
        }

    @staticmethod
    def calculate_weighted_average_rate(
        liabilities: List[Tuple[Decimal, Optional[Decimal]]]
    ) -> Optional[Decimal]:
        """
        Calculates weighted average interest rate across liabilities.
        
        Args:
            liabilities: List of (value, interest_rate) tuples
            
        Returns:
            Weighted average interest rate, or None if no interest-bearing liabilities
        """
        total_value = Decimal('0')
        weighted_sum = Decimal('0')
        for value, rate in liabilities:
            if rate is not None:
                total_value += value
                weighted_sum += value * rate
        if total_value == 0:
            return None
        return weighted_sum / total_value

    @staticmethod
    def project_liability_value(
        current_value: Decimal,
        interest_rate: Optional[Decimal],
        years: int
    ) -> Decimal:
        """
        Projects liability value forward given number of years.
        
        Args:
            current_value: Current liability value
            interest_rate: Optional interest rate
            years: Number of years to project
            
        Returns:
            Projected liability value
        """
        if interest_rate is None:
            return current_value
        return apply_annual_compound_rate(
            current_value,
            interest_rate,
            years
        )

    @staticmethod
    def validate_liability_values(
        liabilities: List[Tuple[int, Decimal]]
    ) -> None:
        """
        Validates all liability values are positive.
        
        Args:
            liabilities: List of (liability_id, value) tuples
            
        Raises:
            ValueError if any value is invalid
        """
        for lid, value in liabilities:
            if value <= 0:
                raise ValueError(
                    f"Liability {lid} has invalid value: {value}"
                )

    
    @staticmethod
    def calculate_total_interest(
        results: List[Tuple[Decimal, Decimal]]
    ) -> Decimal:
        """
        Calculates total interest across all interest-bearing liabilities.
        Args:
            results: List of (starting_value, ending_value) tuples
        Returns:
            Total interest amount
        """
        return sum(
            ending - starting
            for starting, ending in results
        )
    @staticmethod
    def identify_fixed_value_liabilities(
        liabilities: List[Tuple[int, Optional[Decimal]]]
    ) -> List[int]:
        """
        Returns list of liability IDs with no interest rate.
        Args:
            liabilities: List of (liability_id, interest_rate) tuples
        Returns:
            List of liability IDs with fixed values
        """
        return [
            lid for lid, rate in liabilities
            if rate is None
        ]
    @staticmethod
    def identify_high_interest_liabilities(
        liabilities: List[Tuple[int, Optional[Decimal]]],
        threshold: Decimal
    ) -> List[int]:
        """
        Returns list of liability IDs with interest rates above threshold.
        Args:
            liabilities: List of (liability_id, interest_rate) tuples
            threshold: Interest rate threshold
        Returns:
            List of liability IDs with high interest rates
        """
        return [
            lid for lid, rate in liabilities
            if rate and rate > threshold
        ]