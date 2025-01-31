@dataclass
class ScenarioFact:
    """Contains base facts clone plus scenario-specific overrides and retirement spending."""

@dataclass
class ScenarioAssumptions:
    """Scenario-specific overrides of base assumptions including retirement spending."""

@dataclass
class ScenarioCalculationResult:
    """Results container including base fact results plus scenario-specific impacts."""


class ScenarioCalculator:
    def calculate_scenario_year(self, scenario: ScenarioFact, year: int, base_result: YearlyCalculationResult) -> ScenarioCalculationResult:
        """Calculates scenario values starting from base fact results."""

    def apply_scenario_overrides(self, base_result: YearlyCalculationResult, scenario: ScenarioFact) -> ScenarioCalculationResult:
        """Applies scenario-specific overrides to base calculations."""

    def calculate_retirement_spending(self, scenario: ScenarioFact, year: int, inflation_rate: Decimal) -> Decimal:
        """Calculates inflation-adjusted retirement spending amount."""

    def validate_scenario_facts(self, scenario: ScenarioFact) -> None:
        """Validates scenario inputs and overrides before calculations."""
