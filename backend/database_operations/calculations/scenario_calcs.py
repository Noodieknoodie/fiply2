"""
## Scenarios
- Clone of base facts
- Inherits all base facts and base assumptions
- Can override any base fact as well as the fact's parameters
- Unique: Has retirement spending
- Retirement spending:
  - Starts at retirement year
  - Always inflation adjusted
  - Common use: Max sustainable spend

## Base Facts Aggregation
Base facts must remain unchanged while scenarios can modify:
- Asset values and growth
- Liability values and interest
- Cash flow amounts and timing
- Retirement income amounts and timing
- Base assumptions

## Value Display Principles
- All values shown in current dollars
- Inflation adjustments compound annually

Key features of this implementation:
1. Proper inheritance of base facts
2. Support for all types of overrides
3. Always-inflating retirement spending
4. Clear tracking of override impacts
5. Maintains base fact integrity
6. Comprehensive validation
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from copy import deepcopy

from ..models import Scenario, ScenarioAssumption, ScenarioOverride
from .base_facts.base_facts_calcs import (
    BaseFacts,
    YearlyCalculationResult,
    PortfolioValues,
    CashFlowResults,
    IncomeResults

)
from ..utils.money_utils import to_decimal, apply_annual_inflation



@dataclass
class ScenarioFact:
    """Contains scenario-specific data and overrides."""
    scenario_id: int
    name: str
    base_facts: BaseFacts
    retirement_spending: Decimal
    assumption_overrides: Optional[ScenarioAssumption]
    component_overrides: List[ScenarioOverride]


@dataclass
class ScenarioAssumptions:
    """Scenario-specific overrides of base assumptions."""
    retirement_age_1: Optional[int]
    retirement_age_2: Optional[int]
    default_growth_rate: Optional[Decimal]
    inflation_rate: Optional[Decimal]


@dataclass
class ScenarioCalculationResult:
    """Results container including base and scenario-specific impacts."""
    base_result: YearlyCalculationResult
    scenario_portfolio: PortfolioValues
    retirement_spending: Decimal
    adjusted_spending: Decimal
    spending_impact: Decimal
    override_impacts: Dict[str, Decimal]
    metadata: Dict


class ScenarioCalculator:
    """Handles scenario calculations with overrides and retirement spending."""

    def calculate_scenario_year(
        self,
        scenario: ScenarioFact,
        year: int,
        base_result: YearlyCalculationResult,
        prior_scenario_result: Optional[ScenarioCalculationResult] = None
    ) -> ScenarioCalculationResult:
        """Calculates scenario values starting from base fact results."""
        scenario_portfolio = deepcopy(base_result.ending_portfolio)

        override_impacts = self._apply_component_overrides(
            scenario_portfolio,
            scenario.component_overrides,
            year
        )

        retirement_spending, adjusted_spending, spending_impact = Decimal('0'), Decimal('0'), Decimal('0')

        if self._is_retirement_spending_active(scenario, year):
            retirement_spending = scenario.retirement_spending
            years_from_start = year - scenario.base_facts.start_year
            adjusted_spending = apply_annual_inflation(
                retirement_spending,
                self._get_inflation_rate(scenario),
                years_from_start
            )
            spending_impact = adjusted_spending - retirement_spending
            scenario_portfolio = self._apply_retirement_spending(scenario_portfolio, adjusted_spending)

        return ScenarioCalculationResult(
            base_result=base_result,
            scenario_portfolio=scenario_portfolio,
            retirement_spending=retirement_spending,
            adjusted_spending=adjusted_spending,
            spending_impact=spending_impact,
            override_impacts=override_impacts,
            metadata=self._generate_calculation_metadata(
                scenario,
                year,
                override_impacts,
                spending_impact
            )
        )

    def _apply_component_overrides(
        self,
        portfolio: PortfolioValues,
        overrides: List[ScenarioOverride],
        year: int
    ) -> Dict[str, Decimal]:
        """Applies component overrides and tracks their impacts."""
        impacts = {
            'asset_value': Decimal('0'),
            'liability_value': Decimal('0'),
            'cash_flow': Decimal('0'),
            'retirement_income': Decimal('0')
        }

        for override in overrides:
            original_value = self._get_original_value(portfolio, override)
            new_value = to_decimal(override.override_value)
            impact = new_value - original_value

            if override.asset_id:
                impacts['asset_value'] += impact
                portfolio.asset_values[override.asset_id] = new_value
            elif override.liability_id:
                impacts['liability_value'] += impact
                portfolio.liability_values[override.liability_id] = new_value

        return impacts

    def _apply_retirement_spending(
        self,
        portfolio: PortfolioValues,
        spending_amount: Decimal
    ) -> PortfolioValues:
        """Applies retirement spending to portfolio values."""
        portfolio.retirement_portfolio_value -= spending_amount
        return self._update_portfolio_totals(portfolio)

    def _is_retirement_spending_active(
        self,
        scenario: ScenarioFact,
        year: int
    ) -> bool:
        """Determines if retirement spending applies for the year."""
        retirement_year = (
            scenario.assumption_overrides.retirement_age_1
            if scenario.assumption_overrides and scenario.assumption_overrides.retirement_age_1
            else scenario.base_facts.retirement_year
        )
        return year >= retirement_year

    def _get_inflation_rate(
        self,
        scenario: ScenarioFact
    ) -> Decimal:
        """Gets applicable inflation rate considering overrides."""
        if (scenario.assumption_overrides and
            scenario.assumption_overrides.inflation_rate is not None):
            return scenario.assumption_overrides.inflation_rate
        return to_decimal(scenario.base_facts.base_assumptions.inflation_rate)

    def _get_original_value(
        self,
        portfolio: PortfolioValues,
        override: ScenarioOverride
    ) -> Decimal:
        """Retrieves original value for an override target."""
        if override.asset_id:
            return portfolio.asset_values.get(override.asset_id, Decimal('0'))
        elif override.liability_id:
            return portfolio.liability_values.get(override.liability_id, Decimal('0'))
        return Decimal('0')

    def _update_portfolio_totals(
        self,
        portfolio: PortfolioValues
    ) -> PortfolioValues:
        """Updates all portfolio totals after changes."""
        portfolio.total_net_worth = (
            sum(portfolio.asset_values.values()) -
            sum(portfolio.liability_values.values())
        )
        return portfolio

    def _generate_calculation_metadata(
        self,
        scenario: ScenarioFact,
        year: int,
        override_impacts: Dict[str, Decimal],
        spending_impact: Decimal
    ) -> Dict:
        """Creates metadata about scenario calculations."""
        return {
            'scenario_name': scenario.name,
            'year': year,
            'override_count': len(scenario.component_overrides),
            'total_override_impact': sum(override_impacts.values()),
            'spending_impact': spending_impact
        }

    def validate_scenario_facts(
        self,
        scenario: ScenarioFact
    ) -> None:
        """Validates scenario inputs before calculations."""
        if scenario.retirement_spending < 0:
            raise ValueError("Retirement spending cannot be negative")

        if scenario.assumption_overrides:
            if scenario.assumption_overrides.retirement_age_1 is not None and scenario.assumption_overrides.retirement_age_1 < 0:
                raise ValueError("Invalid retirement age override")

        for override in scenario.component_overrides:
            if not any([override.asset_id, override.liability_id, override.inflow_outflow_id, override.retirement_income_plan_id]):
                raise ValueError(f"Override {override.override_id} has no target")

    def generate_override_summary(
        self,
        scenario: ScenarioFact
    ) -> Dict[str, int]:
        """Generates summary of override usage."""
        summary = {
            'asset_overrides': 0,
            'liability_overrides': 0,
            'cash_flow_overrides': 0,
            'retirement_income_overrides': 0
        }

        for override in scenario.component_overrides:
            if override.asset_id:
                summary['asset_overrides'] += 1
            elif override.liability_id:
                summary['liability_overrides'] += 1
            elif override.inflow_outflow_id:
                summary['cash_flow_overrides'] += 1
            elif override.retirement_income_plan_id:
                summary['retirement_income_overrides'] += 1

        return summary
