
“””
## Liabilities
- Value  
- Optional category assignment  
- Optional interest rate  
- Fixed value if no rate specified  
- No default growth rate usage, not affected by it

## Annual Calculation Order
7. Apply liability interest
8. Calculate year-end total

Important Note: The key difference from assets is the simpler growth model - liabilities don't use the default growth rate system at all.
“””

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional

from ..models import Liability
from ..utils.money_utils import to_decimal, apply_annual_compound_rate

@dataclass
class LiabilityFact:
    """Core liability data including value and optional interest rate."""
    liability_id: int
    value: Decimal
    category_id: int
    interest_rate: Optional[Decimal]
    include_in_nest_egg: bool
    owner: str
    name: str

@dataclass
class LiabilityCalculationResult:
    """Results container for liability calculations."""
    liability_id: int
    starting_value: Decimal
    ending_value: Decimal
    interest_amount: Decimal
    category_id: int
    applied_interest_rate: Optional[Decimal]
    included_in_nest_egg: bool
    metadata: Dict

class LiabilityCalculator:
    """Handles liability value calculations with simple interest model."""
    
    def calculate_liability_value(
        self,
        liability: LiabilityFact,
        year: int
    ) -> LiabilityCalculationResult:
        """
        Calculates liability value for a specific year applying interest if specified.
        
        Args:
            liability: Liability data container
            year: Year to calculate for (needed for metadata)
            
        Returns:
            Calculation results including starting/ending values and metadata
        """
        starting_value = liability.value
        interest_amount = Decimal('0')
        
        # Apply interest if specified
        if liability.interest_rate is not None:
            ending_value = apply_annual_compound_rate(
                starting_value,
                liability.interest_rate
            )
            interest_amount = ending_value - starting_value
        else:
            # Fixed value if no interest rate
            ending_value = starting_value
            
        return LiabilityCalculationResult(
            liability_id=liability.liability_id,
            starting_value=starting_value,
            ending_value=ending_value,
            interest_amount=interest_amount,
            category_id=liability.category_id,
            applied_interest_rate=liability.interest_rate,
            included_in_nest_egg=liability.include_in_nest_egg,
            metadata=self._generate_calculation_metadata(
                liability,
                year,
                interest_amount
            )
        )

    def calculate_multiple_liabilities(
        self,
        liabilities: List[LiabilityFact],
        year: int
    ) -> List[LiabilityCalculationResult]:
        """
        Calculates values for multiple liabilities.
        
        Args:
            liabilities: List of liabilities to calculate
            year: Year to calculate for
            
        Returns:
            List of calculation results for each liability
        """
        return [
            self.calculate_liability_value(liability, year)
            for liability in liabilities
        ]

    def aggregate_by_category(
        self,
        results: List[LiabilityCalculationResult]
    ) -> Dict[int, Decimal]:
        """
        Groups and totals liabilities by their categories.
        
        Args:
            results: List of liability calculation results
            
        Returns:
            Dictionary mapping category_id to total value
        """
        totals = {}
        for result in results:
            cat_id = result.category_id
            if cat_id not in totals:
                totals[cat_id] = Decimal('0')
            totals[cat_id] += result.ending_value
        return totals

    def calculate_nest_egg_total(
        self,
        results: List[LiabilityCalculationResult]
    ) -> Decimal:
        """
        Calculates total for liabilities included in retirement portfolio.
        
        Args:
            results: List of liability calculation results
            
        Returns:
            Total value of retirement portfolio liabilities
        """
        return sum(
            r.ending_value 
            for r in results 
            if r.included_in_nest_egg
        )

    def calculate_total_interest(
        self,
        results: List[LiabilityCalculationResult]
    ) -> Decimal:
        """
        Calculates total interest charged across all liabilities.
        
        Args:
            results: List of liability calculation results
            
        Returns:
            Total interest amount
        """
        return sum(r.interest_amount for r in results)

    def _generate_calculation_metadata(
        self,
        liability: LiabilityFact,
        year: int,
        interest_amount: Decimal
    ) -> Dict:
        """Creates metadata about calculation process."""
        return {
            'liability_name': liability.name,
            'owner': liability.owner,
            'year': year,
            'has_interest_rate': liability.interest_rate is not None,
            'interest_amount': str(interest_amount),
            'is_fixed_value': liability.interest_rate is None
        }

    def validate_liability_facts(
        self,
        liabilities: List[LiabilityFact]
    ) -> None:
        """Validates liability inputs before calculations."""
        for liability in liabilities:
            # Validate value is positive
            if liability.value < 0:
                raise ValueError(
                    f"Liability {liability.liability_id} has negative value"
                )
            
            # Validate interest rate if specified
            if liability.interest_rate is not None:
                if liability.interest_rate < 0:
                    raise ValueError(
                        f"Liability {liability.liability_id} has negative interest rate"
                    )

    def get_fixed_value_liabilities(
        self,
        results: List[LiabilityCalculationResult]
    ) -> List[LiabilityCalculationResult]:
        """
        Returns list of liabilities with no interest rate (fixed value).
        
        Args:
            results: List of liability calculation results
            
        Returns:
            Filtered list of fixed-value liabilities
        """
        return [
            r for r in results 
            if r.applied_interest_rate is None
        ]

    def get_interest_bearing_liabilities(
        self,
        results: List[LiabilityCalculationResult]
    ) -> List[LiabilityCalculationResult]:
        """
        Returns list of liabilities with interest rates applied.
        
        Args:
            results: List of liability calculation results
            
        Returns:
            Filtered list of interest-bearing liabilities
        """
        return [
            r for r in results 
            if r.applied_interest_rate is not None
        ]
