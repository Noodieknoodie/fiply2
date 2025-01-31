"""
The key difference from assets is the simpler growth model, as specified in documentation:
md
## Liabilities
- Value  
- Optional interest rate  
- Fixed value if no rate specified  
- No default growth rate usage, not affected by it
"""

@dataclass
class LiabilityFact:
    """Core liability data including value, optional interest rate, and categorization."""

@dataclass
class InterestConfig:
    """Interest rate configuration for liability growth calculations."""

@dataclass
class LiabilityCalculationResult:
    """Results container for liability calculations including current and projected values."""


class LiabilityCalculator:
    def calculate_liability_value(self, liability: LiabilityFact, year: int) -> LiabilityCalculationResult:
        """Calculates liability value for year, applying interest if specified."""

    def aggregate_by_category(self, liabilities: List[LiabilityFact], year: int) -> Dict[str, Decimal]:
        """Groups and totals liabilities by their categories."""

    def calculate_nest_egg_total(self, liabilities: List[LiabilityFact], year: int) -> Decimal:
        """Calculates total for liabilities included in retirement portfolio."""

    def validate_liability_facts(self, liabilities: List[LiabilityFact]) -> None:
        """Validates liability inputs before calculations."""
