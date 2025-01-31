# Growth Rate System
# - The base facts establish a default growth rate
# - Individual assets can override this in several ways:
#   - Simple growth rate override
#   - Stepwise growth rate overrides
#   - Default fallback for uncovered periods
# Single Source of Truth
# - Store values as entered by the user and convert as needed
# - All calculations reference absolute years internally

def get_applicable_growth_rate(year: int, default_rate: float, stepwise_configs: List[Dict]) -> float:
    """Determine which growth rate applies for a given year based on configuration hierarchy."""

def calculate_stepwise_growth(principal: Decimal, configs: List[Dict], start_year: int, end_year: int, default_rate: float) -> Decimal:
    """Calculate total growth across multiple stepwise periods, falling back to default rate when needed."""

def interpolate_missing_periods(stepwise_configs: List[Dict], start_year: int, end_year: int) -> List[Dict]:
    """Fill gaps in stepwise configurations with default rate periods."""