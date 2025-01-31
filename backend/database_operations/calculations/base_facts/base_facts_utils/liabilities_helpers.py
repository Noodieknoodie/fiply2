def _apply_interest(self, value: Decimal, rate: Decimal) -> Decimal:
    """Applies simple interest for one year period."""

def _is_interest_applicable(self, liability: LiabilityFact) -> bool:
    """Determines if liability has valid interest rate configuration."""

def _validate_interest_rate(self, rate: Optional[Decimal]) -> None:
    """Validates interest rate is within acceptable bounds if specified."""

def _calculate_category_totals(self, results: List[LiabilityCalculationResult]) -> Dict[str, Decimal]:
    """Computes running totals by category."""

def _generate_calculation_metadata(self, liability: LiabilityFact, result: LiabilityCalculationResult) -> Dict:
    """Creates metadata about liability calculation for debugging/validation."""