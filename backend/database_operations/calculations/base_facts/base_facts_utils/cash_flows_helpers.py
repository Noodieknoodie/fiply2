"""
## Scheduled Inflows/Outflows
- Start year, end year (stored as entered but converted as needed)
- Amount
- Optional inflation toggle
- For discrete events only
- Input in years
- Examples: College (start year, end year different), inheritance (start year, end year the same)

## Value Display Principles
- All values shown in current dollars
- Inflation adjustments compound annually
- No partial year or day counting
- No cash flow timing within year
- All events assumed to occur at year boundaries
"""

from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from enum import Enum

from ....utils.money_utils import to_decimal, apply_annual_inflation

class FlowType(Enum):
    """Enumeration for flow types."""
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'

class CashFlowCalculationHelpers:
    """Specialized helper methods for cash flow calculations."""
    
    @staticmethod
    def is_flow_active(
        flow_start_year: int,
        flow_end_year: Optional[int],
        current_year: int
    ) -> Tuple[bool, str]:
        """
        Determines if flow is active based on start/end years.
        
        Args:
            flow_start_year: Year flow begins
            flow_end_year: Optional year flow ends
            current_year: Year to check
            
        Returns:
            Tuple of (is_active, reason)
        """
        actual_end = flow_end_year or flow_start_year
        
        if current_year < flow_start_year:
            return False, "before_start"
        
        if current_year > actual_end:
            return False, "after_end"
            
        return True, "active"

    @staticmethod
    def apply_inflation_adjustment(
        amount: Decimal,
        inflation_rate: Decimal,
        years_from_start: int,
        apply_inflation: bool
    ) -> Tuple[Decimal, Decimal]:
        """
        Applies compound inflation adjustment if enabled.
        
        Args:
            amount: Base amount
            inflation_rate: Annual inflation rate
            years_from_start: Years since plan start
            apply_inflation: Whether to apply inflation
            
        Returns:
            Tuple of (adjusted_amount, inflation_impact)
        """
        if not apply_inflation or years_from_start == 0:
            return amount, Decimal('0')
            
        adjusted = apply_annual_inflation(
            amount,
            inflation_rate,
            years_from_start
        )
        return adjusted, (adjusted - amount)

    @staticmethod
    def validate_year_boundaries(
        start_year: int,
        end_year: Optional[int],
        plan_start_year: int,
        plan_end_year: int
    ) -> None:
        """
        Validates start/end years are chronological and valid.
        
        Args:
            start_year: Flow start year
            end_year: Optional flow end year
            plan_start_year: First year of plan
            plan_end_year: Last year of plan
            
        Raises:
            ValueError if years are invalid
        """
        if start_year < plan_start_year:
            raise ValueError(
                f"Flow start year {start_year} before plan start year {plan_start_year}"
            )
            
        actual_end = end_year or start_year
        
        if actual_end > plan_end_year:
            raise ValueError(
                f"Flow end year {actual_end} after plan end year {plan_end_year}"
            )
            
        if end_year and start_year > end_year:
            raise ValueError(
                f"Flow start year {start_year} after end year {end_year}"
            )

    @staticmethod
    def generate_flow_metadata(
        flow_id: int,
        flow_type: FlowType,
        base_amount: Decimal,
        adjusted_amount: Decimal,
        year: int,
        is_active: bool,
        inflation_applied: bool
    ) -> Dict:
        """
        Creates metadata about flow calculation.
        
        Args:
            flow_id: ID of cash flow
            flow_type: Type of flow (inflow/outflow)
            base_amount: Original amount
            adjusted_amount: Inflation-adjusted amount
            year: Calculation year
            is_active: Whether flow was active
            inflation_applied: Whether inflation was applied
            
        Returns:
            Dictionary containing calculation metadata
        """
        return {
            'flow_id': flow_id,
            'flow_type': flow_type.value,
            'year': year,
            'base_amount': str(base_amount),
            'adjusted_amount': str(adjusted_amount),
            'inflation_impact': str(adjusted_amount - base_amount),
            'is_active': is_active,
            'inflation_applied': inflation_applied
        }

    @staticmethod
    def calculate_type_totals(
        flows: List[Tuple[FlowType, Decimal, bool]]
    ) -> Dict[FlowType, Decimal]:
        """
        Computes running totals by flow type.
        
        Args:
            flows: List of (type, amount, is_active) tuples
            
        Returns:
            Dictionary of totals by flow type
        """
        totals = {
            FlowType.INFLOW: Decimal('0'),
            FlowType.OUTFLOW: Decimal('0')
        }
        
        for flow_type, amount, is_active in flows:
            if is_active:
                totals[flow_type] += amount
                
        return totals

    @staticmethod
    def detect_flow_patterns(
        start_year: int,
        end_year: Optional[int]
    ) -> Dict[str, bool]:
        """
        Analyzes flow pattern type.
        
        Args:
            start_year: Flow start year
            end_year: Optional flow end year
            
        Returns:
            Dictionary describing flow pattern
        """
        actual_end = end_year or start_year
        duration = actual_end - start_year + 1
        
        return {
            'is_single_year': duration == 1,
            'is_multi_year': duration > 1,
            'has_end_date': end_year is not None
        }

    @staticmethod
    def calculate_total_flow_amount(
        annual_amount: Decimal,
        start_year: int,
        end_year: Optional[int],
        inflation_rate: Optional[Decimal] = None,
        apply_inflation: bool = False
    ) -> Decimal:
        """
        Calculates total nominal flow amount over entire period.
        
        Args:
            annual_amount: Annual flow amount
            start_year: Flow start year
            end_year: Optional flow end year
            inflation_rate: Optional inflation rate
            apply_inflation: Whether to apply inflation
            
        Returns:
            Total flow amount
        """
        actual_end = end_year or start_year
        duration = actual_end - start_year + 1
        
        if not apply_inflation or not inflation_rate:
            return annual_amount * duration
            
        total = Decimal('0')
        for year in range(duration):
            adjusted = apply_annual_inflation(
                annual_amount,
                inflation_rate,
                year
            )
            total += adjusted
            
        return total

    @staticmethod
    def validate_flow_amount(
        amount: Decimal,
        flow_type: FlowType
    ) -> None:
        """
        Validates flow amount is positive.
        
        Args:
            amount: Flow amount to validate
            flow_type: Type of flow
            
        Raises:
            ValueError if amount is invalid
        """
        if amount <= 0:
            raise ValueError(
                f"{flow_type.value.capitalize()} amount must be positive"
            )

    @staticmethod
    def categorize_flows(
        flows: List[Tuple[FlowType, Decimal, str]]
    ) -> Dict[str, List[Tuple[FlowType, Decimal]]]:
        """
        Groups flows by their purpose/category.
        
        Args:
            flows: List of (type, amount, category) tuples
            
        Returns:
            Dictionary grouping flows by category
        """
        categories = {}
        
        for flow_type, amount, category in flows:
            if category not in categories:
                categories[category] = []
            categories[category].append((flow_type, amount))
            
        return categories