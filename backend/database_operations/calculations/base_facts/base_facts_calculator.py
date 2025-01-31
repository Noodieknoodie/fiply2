
"""
Annual Calculation Order
1. Start with prior year-end values  
2. Apply scheduled inflows (inflation-adjusted if enabled)  
3. Apply scheduled outflows (inflation-adjusted if enabled)  
4. Apply retirement income  
5. Apply retirement spending  
6. Apply growth rates to remaining balance:  
   - Asset-specific rates first  
   - Default rates to remaining  
7. Apply liability interest  
8. Calculate year-end total  
"""

@dataclass
class BaseFacts:
    """Container for all base fact inputs: assets, liabilities, cash flows, retirement income, and base assumptions. No retirement spending."""

@dataclass
class YearlyCalculationResult:
    """Results container for a single projection year including all portfolio values, cash flows, and running totals."""

@dataclass
class PortfolioValues:
    """Represents portfolio state including assets, liabilities, category totals, and retirement portfolio values."""

@dataclass
class CashFlowResults:
    """Tracks all cash movements for a year including inflation adjustments and running totals."""

@dataclass
class IncomeResults:
    """Records all retirement income streams and their adjustments for a given year."""


# Main Calculator Class

class BaseFactsCalculator:
    def validate_inputs(self, base_facts: BaseFacts) -> None:
        """Validates all base fact inputs before calculation sequence begins."""

    def calculate_year(self, year: int, base_facts: BaseFacts, prior_result: Optional[YearlyCalculationResult]) -> YearlyCalculationResult:
        """Executes annual calculation sequence following strict ordering."""

    def calculate_portfolio_values(self, year: int, base_facts: BaseFacts, prior_values: Optional[PortfolioValues]) -> PortfolioValues:
        """Calculates current portfolio state including all assets and liabilities."""

    def process_cash_flows(self, year: int, base_facts: BaseFacts) -> CashFlowResults:
        """Processes all inflows and outflows, applying inflation where specified."""

    def process_retirement_income(self, year: int, base_facts: BaseFacts) -> IncomeResults:
        """Calculates all retirement income streams for the year."""

    def apply_growth_rates(self, portfolio: PortfolioValues, base_facts: BaseFacts) -> PortfolioValues:
        """Applies growth rates according to hierarchy: asset-specific, stepwise, then default."""
    
    def apply_liability_interest(self, portfolio: PortfolioValues, base_facts: BaseFacts) -> PortfolioValues:
        """Applies interest to liabilities with specified rates."""

    def calculate_year_end_totals(self, portfolio: PortfolioValues) -> Decimal:
        """Computes final portfolio values and category totals for year-end."""

    def generate_projection(self, base_facts: BaseFacts) -> List[YearlyCalculationResult]:
        """Generates complete projection timeline from start to end year."""
