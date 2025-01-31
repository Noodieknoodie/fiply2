def _is_income_active(self, income: RetirementIncomeFact, year: int) -> bool:
    """Determines if income is active based on person's age in given year."""

def _get_year_for_age(self, income: RetirementIncomeFact, target_age: int) -> int:
    """Converts age-based timing to absolute year using DOB."""

def _apply_inflation_adjustment(self, amount: Decimal, inflation_rate: Decimal, years_from_start: int) -> Decimal:
    """Applies compound inflation adjustment if enabled."""

def _validate_age_boundaries(self, income: RetirementIncomeFact) -> None:
    """Validates start/end ages are chronological and valid."""

def _generate_income_metadata(self, income: RetirementIncomeFact, result: IncomeCalculationResult) -> Dict:
    """Creates metadata about income calculation for debugging/validation."""
