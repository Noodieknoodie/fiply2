"""
## Liabilities
- Value  
- Optional category assignment  
- Optional interest rate  
- Fixed value if no rate specified  
- No default growth rate usage, not affected by it

Important Note: The key difference from assets is the simpler growth model - 
liabilities use an optional simple interest rate instead of the complex growth rate system.
"""


from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from datetime import date

from ....utils.money_utils import to_decimal, apply_annual_compound_rate

class LiabilityCalculationHelpers:
    """Specialized helper methods for liability calculations."""
    
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
    def validate_interest_rate(
        rate: Optional[Decimal]
    ) -> None:
        """
        Validates interest rate is within acceptable bounds if specified.
        
        Args:
            rate: Optional interest rate to validate
            
        Raises:
            ValueError if rate is invalid
        """
        if rate is not None and rate < 0:
            raise ValueError("Interest rate cannot be negative")

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