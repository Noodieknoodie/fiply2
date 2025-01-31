def _apply_asset_overrides(self, base_result: YearlyCalculationResult, overrides: Dict) -> PortfolioValues:
    """Applies scenario-specific asset value and growth overrides."""

def _apply_liability_overrides(self, base_result: YearlyCalculationResult, overrides: Dict) -> PortfolioValues:
    """Applies scenario-specific liability value and interest overrides."""

def _apply_cash_flow_overrides(self, base_result: YearlyCalculationResult, overrides: Dict) -> CashFlowResults:
    """Applies scenario-specific cash flow amount and timing overrides."""

def _is_retirement_spending_active(self, scenario: ScenarioFact, year: int) -> bool:
    """Determines if retirement spending applies for given year."""

def _calculate_adjusted_spending(self, base_amount: Decimal, inflation_rate: Decimal, years_from_retirement: int) -> Decimal:
    """Calculates inflation-adjusted retirement spending amount."""

def _generate_scenario_metadata(self, scenario: ScenarioFact, result: ScenarioCalculationResult) -> Dict:
    """Creates metadata about scenario calculations for debugging/validation."""