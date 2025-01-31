
"""
These helper methods support the main calculation sequence while enforcing:
- No intra-year calculations
- Proper growth rate hierarchy
- Clear calculation boundaries
- Strong validation
"""

def _initialize_starting_values(self, base_facts: BaseFacts) -> PortfolioValues:
    """Creates initial portfolio state for first projection year."""

def _carry_forward_values(self, prior_result: YearlyCalculationResult) -> PortfolioValues:
    """Propagates prior year values forward as starting point for new year."""

def _get_applicable_growth_rate(self, asset: Asset, year: int, default_rate: Decimal) -> Decimal:
    """Determines correct growth rate based on asset configuration and timeline."""

def _process_stepwise_growth(self, config: GrowthConfig, year: int, default_rate: Decimal) -> Decimal:
    """Handles stepwise growth periods, falling back to default rate when needed."""

def _calculate_flow_amount(self, flow: CashFlow, year: int, inflation_rate: Decimal) -> Decimal:
    """Calculates cash flow amount with inflation adjustment if enabled."""

def _is_flow_active(self, flow: CashFlow, year: int) -> bool:
    """Determines if a cash flow is active for the given year."""

def _is_income_active(self, income: RetirementIncome, year: int) -> bool:
    """Determines if retirement income is active based on age/year criteria."""

def _update_category_totals(self, values: Dict[int, Decimal], categories: Dict[int, str]) -> Dict[str, Decimal]:
    """Updates running totals for asset/liability categories."""

def _calculate_retirement_portfolio(self, portfolio: PortfolioValues) -> Decimal:
    """Calculates retirement portfolio value including only eligible components."""

def _generate_calculation_metadata(self, year: int, portfolio: PortfolioValues, flows: CashFlowResults) -> Dict:
    """Creates metadata about calculation process for debugging/validation."""

def _validate_timeline(self, year: int, base_facts: BaseFacts) -> None:
    """Ensures calculations stay within valid projection timeline."""

def _validate_growth_configs(self, base_facts: BaseFacts) -> None:
    """Validates all growth rate configurations are properly structured."""

def _validate_rates(self, base_facts: BaseFacts) -> None:
    """Validates all growth, interest, and inflation rates are valid."""
