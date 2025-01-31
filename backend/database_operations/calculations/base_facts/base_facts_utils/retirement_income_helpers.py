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
  """

from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from datetime import date

from ....utils.money_utils import to_decimal, apply_annual_inflation
from ....utils.time_utils import get_age_at_year, get_year_for_age

class RetirementIncomeHelpers:
    """Specialized helper methods for retirement income calculations."""
    
    @staticmethod
    def is_income_active(
        start_age: int,
        end_age: Optional[int],
        person_dob: date,
        current_year: int
    ) -> Tuple[bool, str]:
        """
        Determines if income is active based on person's age in given year.
        
        Args:
            start_age: Age when income begins
            end_age: Optional age when income ends
            person_dob: Date of birth of income recipient
            current_year: Year to check
            
        Returns:
            Tuple of (is_active, reason)
        """
        current_age = get_age_at_year(person_dob, current_year)
        
        if current_age < start_age:
            return False, "before_start_age"
            
        if end_age is not None and current_age > end_age:
            return False, "after_end_age"
            
        return True, "active"

    @staticmethod
    def get_year_for_age(
        target_age: int,
        person_dob: date
    ) -> int:
        """
        Converts age-based timing to absolute year using DOB.
        
        Args:
            target_age: Age to convert to year
            person_dob: Date of birth of income recipient
            
        Returns:
            Year when person reaches target age
        """
        return get_year_for_age(person_dob, target_age)

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
            amount: Base income amount
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
    def validate_age_boundaries(
        start_age: int,
        end_age: Optional[int],
        person_dob: date,
        plan_end_year: int
    ) -> None:
        """
        Validates start/end ages are chronological and valid.
        
        Args:
            start_age: Age when income begins
            end_age: Optional age when income ends
            person_dob: Date of birth of income recipient
            plan_end_year: Last year of plan
            
        Raises:
            ValueError if ages are invalid
        """
        if start_age < 0:
            raise ValueError(f"Invalid start age: {start_age}")
            
        if end_age is not None:
            if end_age < start_age:
                raise ValueError(
                    f"End age {end_age} before start age {start_age}"
                )
                
            end_year = get_year_for_age(person_dob, end_age)
            if end_year > plan_end_year:
                raise ValueError(
                    f"Income extends beyond plan end year"
                )

    @staticmethod
    def generate_income_metadata(
        income_id: int,
        base_amount: Decimal,
        adjusted_amount: Decimal,
        current_age: int,
        is_active: bool,
        year: int
    ) -> Dict:
        """
        Creates metadata about income calculation.
        
        Args:
            income_id: ID of income stream
            base_amount: Original amount
            adjusted_amount: Inflation-adjusted amount
            current_age: Current age of recipient
            is_active: Whether income was active
            year: Calculation year
            
        Returns:
            Dictionary containing calculation metadata
        """
        return {
            'income_id': income_id,
            'year': year,
            'current_age': current_age,
            'base_amount': str(base_amount),
            'adjusted_amount': str(adjusted_amount),
            'inflation_impact': str(adjusted_amount - base_amount),
            'is_active': is_active
        }

    @staticmethod
    def calculate_lifetime_total(
        annual_amount: Decimal,
        start_age: int,
        person_dob: date,
        inflation_rate: Optional[Decimal] = None,
        apply_inflation: bool = False
    ) -> Optional[Decimal]:
        """
        Calculates total lifetime income for streams with no end age.
        
        Args:
            annual_amount: Annual income amount
            start_age: Age when income begins
            person_dob: Date of birth of recipient
            inflation_rate: Optional inflation rate
            apply_inflation: Whether to apply inflation
            
        Returns:
            Total lifetime income or None if calculation not possible
        """
        if not apply_inflation or inflation_rate is None:
            return None  # Cannot calculate without end date
            
        # Use 100 as maximum age for calculation
        MAX_AGE = 100
        duration = MAX_AGE - start_age
        
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
    def categorize_income_streams(
        streams: List[Tuple[str, Decimal, bool]]
    ) -> Dict[str, List[Tuple[Decimal, bool]]]:
        """
        Groups income streams by type.
        
        Args:
            streams: List of (name, amount, is_inflation_adjusted) tuples
            
        Returns:
            Dictionary grouping streams by type
        """
        categories = {}
        
        for name, amount, inflation_adj in streams:
            category = name.split()[0].upper()  # E.g., "Social" from "Social Security"
            
            if category not in categories:
                categories[category] = []
                
            categories[category].append((amount, inflation_adj))
            
        return categories

    @staticmethod
    def calculate_replacement_ratio(
        total_retirement_income: Decimal,
        pre_retirement_income: Decimal
    ) -> Optional[Decimal]:
        """
        Calculates income replacement ratio.
        
        Args:
            total_retirement_income: Total annual retirement income
            pre_retirement_income: Annual income before retirement
            
        Returns:
            Replacement ratio as percentage or None if pre-retirement income is 0
        """
        if pre_retirement_income == 0:
            return None
            
        return (total_retirement_income / pre_retirement_income) * 100

    @staticmethod
    def project_income_stream(
        current_amount: Decimal,
        inflation_rate: Decimal,
        years: int,
        apply_inflation: bool
    ) -> List[Decimal]:
        """
        Projects income stream values forward.
        
        Args:
            current_amount: Current annual amount
            inflation_rate: Annual inflation rate
            years: Number of years to project
            apply_inflation: Whether to apply inflation
            
        Returns:
            List of projected annual amounts
        """
        projections = []
        amount = current_amount
        
        for year in range(years):
            projections.append(amount)
            
            if apply_inflation:
                amount = apply_annual_inflation(
                    amount,
                    inflation_rate,
                    1
                )
                
        return projections