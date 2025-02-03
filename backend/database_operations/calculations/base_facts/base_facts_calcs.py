# backend/database_operations/calculations/base_facts/base_facts_calculator.py
"""
## Annual Calculation Order
1. Start with prior year-end values  
2. Apply scheduled inflows (inflation-adjusted if enabled)  
3. Apply scheduled outflows (inflation-adjusted if enabled)  
4. Apply retirement income  
5. Apply retirement spending  
6. Apply asset growth using `GrowthRateHandler`:  
   - Asset-specific rates applied through `_apply_all_growth`  
   - Default rates applied if no asset-specific rate exists  
7. Apply liability interest  
8. Calculate year-end total  
## Value Display Principles
- All values shown in current dollars
- Inflation adjustments compound annually
- Growth is calculated exclusively via `GrowthRateHandler`  
- No partial year or day counting  
- No cash flow timing within year  
- All events occur at year boundaries  
- Portfolio values represent year-end totals  
## Growth Calculation Updates
- Growth calculations are now centralized in `GrowthRateHandler`  
- `_apply_all_growth` is the single method for applying growth to all assets  
- Liability interest remains separate but follows similar compound application  
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional

from ...models import Asset, Liability, InflowOutflow, RetirementIncomePlan, BaseAssumption
from ...utils.money_utils import to_decimal, apply_annual_compound_rate, apply_annual_inflation
from .growth_handler_calcs import GrowthRateHandler


@dataclass
class BaseFacts:
    """Stores base financial data for projections."""
    assets: List[Asset]
    liabilities: List[Liability]
    inflows_outflows: List[InflowOutflow]
    retirement_income: List[RetirementIncomePlan]
    base_assumptions: BaseAssumption
    start_year: int
    retirement_year: int
    end_year: int


@dataclass
class PortfolioValues:
    """Represents financial portfolio status."""
    asset_values: Dict[int, Decimal]
    liability_values: Dict[int, Decimal]
    asset_category_totals: Dict[str, Decimal]
    liability_category_totals: Dict[str, Decimal]
    retirement_portfolio_value: Decimal
    total_net_worth: Decimal


@dataclass
class CashFlowResults:
    """Tracks cash movements in a given year."""
    inflows: Dict[int, Decimal]
    outflows: Dict[int, Decimal]
    net_inflows: Decimal
    net_outflows: Decimal
    total_net_flow: Decimal


@dataclass
class IncomeResults:
    """Records annual retirement income."""
    income_streams: Dict[int, Decimal]
    total_income: Decimal


@dataclass
class YearlyCalculationResult:
    """Stores full results of an annual projection."""
    year: int
    starting_portfolio: PortfolioValues
    cash_flows: CashFlowResults
    income: IncomeResults
    ending_portfolio: PortfolioValues
    metadata: Dict


class BaseFactsCalculator:
    """Executes annual financial projections."""

    def __init__(self):
        self.growth_handler = GrowthRateHandler()

    def calculate_year(self, year: int, base_facts: BaseFacts,
                       prior_result: Optional[YearlyCalculationResult]) -> YearlyCalculationResult:
        """Computes portfolio projections for a given year."""
        starting_portfolio = self._carry_forward_values(prior_result) if prior_result else self._initialize_starting_values(base_facts)
        cash_flows = self.process_cash_flows(year, base_facts)
        income = self.process_retirement_income(year, base_facts)
        interim_portfolio = self._apply_flows_to_portfolio(starting_portfolio, cash_flows, income, base_facts)
        grown_portfolio = self._apply_all_growth(interim_portfolio, year, base_facts)
        final_portfolio = self.apply_liability_interest(grown_portfolio, base_facts)
        final_portfolio = self._update_portfolio_totals(final_portfolio, base_facts)

        return YearlyCalculationResult(
            year=year,
            starting_portfolio=starting_portfolio,
            cash_flows=cash_flows,
            income=income,
            ending_portfolio=final_portfolio,
            metadata=self._generate_calculation_metadata(year, final_portfolio, cash_flows)
        )

    def _apply_all_growth(self, portfolio: PortfolioValues, year: int, base_facts: BaseFacts) -> PortfolioValues:
        """Applies growth to all assets."""
        for asset in base_facts.assets:
            growth_result = self.growth_handler.apply_growth(
                portfolio.asset_values[asset.asset_id],
                asset.asset_id,
                year,
                to_decimal(base_facts.base_assumptions.default_growth_rate),
                asset.growth_rates
            )
            portfolio.asset_values[asset.asset_id] = growth_result.final_value

        return self._update_portfolio_totals(portfolio, base_facts)

    def apply_liability_interest(self, portfolio: PortfolioValues, base_facts: BaseFacts) -> PortfolioValues:
        """Applies interest to liabilities."""
        for liability in base_facts.liabilities:
            if liability.interest_rate:
                portfolio.liability_values[liability.liability_id] = apply_annual_compound_rate(
                    portfolio.liability_values[liability.liability_id], to_decimal(liability.interest_rate)
                )
        return self._update_portfolio_totals(portfolio, base_facts)

    def process_cash_flows(self, year: int, base_facts: BaseFacts) -> CashFlowResults:
        """Calculates cash inflows and outflows for a year."""
        inflows, outflows = {}, {}

        for flow in base_facts.inflows_outflows:
            if flow.start_year <= year <= (flow.end_year or flow.start_year):
                amount = to_decimal(flow.annual_amount)
                if flow.apply_inflation:
                    amount = apply_annual_inflation(amount, to_decimal(base_facts.base_assumptions.inflation_rate),
                                                    year - base_facts.start_year)
                (inflows if flow.type == 'inflow' else outflows)[flow.inflow_outflow_id] = amount

        return CashFlowResults(
            inflows=inflows,
            outflows=outflows,
            net_inflows=sum(inflows.values()),
            net_outflows=sum(outflows.values()),
            total_net_flow=sum(inflows.values()) - sum(outflows.values())
        )

    def process_retirement_income(self, year: int, base_facts: BaseFacts) -> IncomeResults:
        """Computes retirement income for a year."""
        if year < base_facts.retirement_year:
            return IncomeResults(income_streams={}, total_income=Decimal('0'))

        income_streams = {income.income_plan_id: to_decimal(income.annual_income) for income in base_facts.retirement_income
                          if self._is_income_active(income, year)}

        return IncomeResults(
            income_streams=income_streams,
            total_income=sum(income_streams.values())
        )

    def _update_portfolio_totals(self, portfolio: PortfolioValues, base_facts: BaseFacts) -> PortfolioValues:
        """Updates portfolio totals including net worth and category values."""
        portfolio.total_net_worth = sum(portfolio.asset_values.values()) - sum(portfolio.liability_values.values())
        portfolio.retirement_portfolio_value = sum(value for asset in base_facts.assets
                                                   if asset.include_in_nest_egg and (value := portfolio.asset_values[asset.asset_id]))

        portfolio.asset_category_totals = {asset.asset_category_id: sum(portfolio.asset_values[a.asset_id]
                                                                         for a in base_facts.assets
                                                                         if a.asset_category_id == asset.asset_category_id)
                                           for asset in base_facts.assets}

        portfolio.liability_category_totals = {liability.liability_category_id: sum(portfolio.liability_values[l.liability_id]
                                                                                    for l in base_facts.liabilities
                                                                                    if l.liability_category_id == liability.liability_category_id)
                                               for liability in base_facts.liabilities}
        return portfolio

    def _apply_flows_to_portfolio(self, portfolio: PortfolioValues, cash_flows: CashFlowResults, income: IncomeResults,
                                  base_facts: BaseFacts) -> PortfolioValues:
        """Adjusts portfolio for cash flow and income events."""
        portfolio.retirement_portfolio_value += sum(cash_flows.inflows.values()) - sum(cash_flows.outflows.values()) + income.total_income
        return self._update_portfolio_totals(portfolio, base_facts)

    def generate_projection(self, base_facts: BaseFacts) -> List[YearlyCalculationResult]:
        """Generates complete financial projection timeline."""
        self.validate_inputs(base_facts)
        results, prior_result = [], None

        for year in range(base_facts.start_year, base_facts.end_year + 1):
            result = self.calculate_year(year, base_facts, prior_result)
            results.append(result)
            prior_result = result

        return results

    def validate_inputs(self, base_facts: BaseFacts) -> None:
        """Ensures all financial inputs are valid."""
        if not base_facts.assets and not base_facts.liabilities:
            raise ValueError("At least one asset or liability is required.")
        if base_facts.start_year >= base_facts.retirement_year or base_facts.retirement_year >= base_facts.end_year:
            raise ValueError("Invalid timeline sequence.")

    def _is_income_active(self, income: RetirementIncomePlan, year: int) -> bool:
        """Checks if a retirement income stream is active in a given year."""
        return income.start_year <= year <= (income.end_year or income.start_year)

    def _generate_calculation_metadata(self, year: int, portfolio: PortfolioValues, flows: CashFlowResults) -> Dict:
        """Creates metadata about a given year's calculations."""
        return {
            "year": year,
            "total_inflows": flows.net_inflows,
            "total_outflows": flows.net_outflows,
            "ending_portfolio_value": portfolio.retirement_portfolio_value
        }
