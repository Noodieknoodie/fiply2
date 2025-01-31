def _is_flow_active(self, flow: CashFlowFact, year: int) -> bool:
    """Determines if flow is active based on start/end years."""

def _apply_inflation_adjustment(self, amount: Decimal, inflation_rate: Decimal, years: int) -> Decimal:
    """Applies compound inflation adjustment if enabled."""

def _validate_year_boundaries(self, flow: CashFlowFact) -> None:
    """Validates start/end years are chronological and valid."""

def _generate_flow_metadata(self, flow: CashFlowFact, result: CashFlowCalculationResult) -> Dict:
    """Creates metadata about flow calculation for debugging/validation."""

def _calculate_type_totals(self, results: List[CashFlowCalculationResult]) -> Dict[str, Decimal]:
    """Computes running totals by flow type (inflow/outflow)."""
