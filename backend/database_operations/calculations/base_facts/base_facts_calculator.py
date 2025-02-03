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
from typing import List, Optional, Dict
from datetime import date

from ...models import Asset, Liability, InflowOutflow, RetirementIncomePlan, BaseAssumption
from ...utils.money_utils import (
    to_decimal, 
    apply_annual_compound_rate,
    apply_annual_inflation
)
from growth_handler_calcs import GrowthRateHandler


@dataclass
class BaseFacts:
    """Container for all base fact inputs."""
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
    """Represents portfolio state at a point in time."""
    asset_values: Dict[int, Decimal]  # asset_id -> value
    liability_values: Dict[int, Decimal]  # liability_id -> value
    asset_category_totals: Dict[str, Decimal]  # category -> total
    liability_category_totals: Dict[str, Decimal]  # category -> total
    retirement_portfolio_value: Decimal
    total_net_worth: Decimal

@dataclass
class CashFlowResults:
    """Tracks all cash movements for a year."""
    inflows: Dict[int, Decimal]  # flow_id -> adjusted_amount
    outflows: Dict[int, Decimal]  # flow_id -> adjusted_amount
    net_inflows: Decimal
    net_outflows: Decimal
    total_net_flow: Decimal

@dataclass
class IncomeResults:
    """Records retirement income for a year."""
    income_streams: Dict[int, Decimal]  # income_id -> adjusted_amount
    total_income: Decimal

@dataclass
class YearlyCalculationResult:
    """Complete results for a single projection year."""
    year: int
    starting_portfolio: PortfolioValues
    cash_flows: CashFlowResults
    income: IncomeResults
    ending_portfolio: PortfolioValues
    metadata: Dict  # For debugging/validation

class BaseFactsCalculator:
    """Executes annual calculation sequence following strict ordering."""
    
    def __init__(self):
        self.growth_handler = GrowthRateHandler()
    
    def calculate_year(
        self, 
        year: int, 
        base_facts: BaseFacts,
        prior_result: Optional[YearlyCalculationResult]
    ) -> YearlyCalculationResult:
        """Executes complete calculation sequence for one year."""
        # Start with prior values or initialize
        if prior_result:
            starting_portfolio = self._carry_forward_values(prior_result)
        else:
            starting_portfolio = self._initialize_starting_values(base_facts)

        # Process cash flows
        cash_flows = self.process_cash_flows(year, base_facts)
        
        # Process retirement income if after retirement
        income = self.process_retirement_income(year, base_facts)
        
        # Apply cash flows and income to portfolio
        interim_portfolio = self._apply_flows_to_portfolio(
            starting_portfolio,
            cash_flows,
            income,
            base_facts
        )
        
        # Apply asset growth via `_apply_all_growth`
        grown_portfolio = self._apply_all_growth(
            interim_portfolio,
            year,
            base_facts
        )
        
        # Apply liability interest
        final_portfolio = self.apply_liability_interest(
            grown_portfolio,
            base_facts
        )
        
        # Calculate final totals
        final_portfolio = self._update_portfolio_totals(final_portfolio, base_facts)
        
        return YearlyCalculationResult(
            year=year,
            starting_portfolio=starting_portfolio,
            cash_flows=cash_flows,
            income=income,
            ending_portfolio=final_portfolio,
            metadata=self._generate_calculation_metadata(
                year, 
                final_portfolio,
                cash_flows
            )
        )
    
    def _apply_all_growth(
        self,
        portfolio: PortfolioValues,
        year: int,
        base_facts: BaseFacts
    ) -> PortfolioValues:
        """Applies growth to all assets using GrowthRateHandler."""
        new_values = portfolio.asset_values.copy()
        
        for asset_id, value in portfolio.asset_values.items():
            asset = next(a for a in base_facts.assets if a.asset_id == asset_id)
            
            growth_result = self.growth_handler.apply_growth(
                value,
                asset_id,
                year,
                to_decimal(base_facts.base_assumptions.default_growth_rate),
                asset.growth_rates
            )
            
            new_values[asset_id] = growth_result.final_value
        
        portfolio.asset_values = new_values
        return self._update_portfolio_totals(portfolio, base_facts)



    def apply_liability_interest(
        self,
        portfolio: PortfolioValues,
        base_facts: BaseFacts
    ) -> PortfolioValues:
        """Applies interest to liabilities with specified rates."""
        new_values = portfolio.liability_values.copy()

        for liability_id, value in portfolio.liability_values.items():
            liability = next(
                l for l in base_facts.liabilities 
                if l.liability_id == liability_id
            )

            if liability.interest_rate:
                rate = to_decimal(liability.interest_rate)
                new_values[liability_id] = apply_annual_compound_rate(value, rate)

        portfolio.liability_values = new_values
        return self._update_portfolio_totals(portfolio, base_facts)

    def _update_portfolio_totals(self, portfolio: PortfolioValues, base_facts: BaseFacts) -> PortfolioValues:
        """Updates all running totals."""
        # Calculate total net worth
        portfolio.total_net_worth = (
            sum(portfolio.asset_values.values()) -
            sum(portfolio.liability_values.values())
        )

        # Calculate retirement portfolio value (nest egg only)
        portfolio.retirement_portfolio_value = sum(
            value for asset_id, value in portfolio.asset_values.items()
            if next(a for a in base_facts.assets if a.asset_id == asset_id).include_in_nest_egg
        )

        # Calculate asset category totals
        portfolio.asset_category_totals = {}
        for asset in base_facts.assets:
            if asset.asset_category_id not in portfolio.asset_category_totals:
                portfolio.asset_category_totals[asset.asset_category_id] = Decimal('0')
            portfolio.asset_category_totals[asset.asset_category_id] += portfolio.asset_values[asset.asset_id]

        # Calculate liability category totals
        portfolio.liability_category_totals = {}
        for liability in base_facts.liabilities:
            if liability.liability_category_id not in portfolio.liability_category_totals:
                portfolio.liability_category_totals[liability.liability_category_id] = Decimal('0')
            portfolio.liability_category_totals[liability.liability_category_id] += portfolio.liability_values[liability.liability_id]

        return portfolio

    def process_cash_flows(self, year: int, base_facts: BaseFacts) -> CashFlowResults:
        """Processes all inflows and outflows for the year."""
        inflows = {}
        outflows = {}

        for flow in base_facts.inflows_outflows:
            if not (flow.start_year <= year <= (flow.end_year or flow.start_year)):
                continue

            amount = to_decimal(flow.annual_amount)

            if flow.apply_inflation:
                years_from_start = year - base_facts.start_year
                amount = apply_annual_inflation(
                    amount,
                    to_decimal(base_facts.base_assumptions.inflation_rate),
                    years_from_start
                )

            if flow.type == 'inflow':
                inflows[flow.inflow_outflow_id] = amount
            else:
                outflows[flow.inflow_outflow_id] = amount

        net_inflows = sum(inflows.values())
        net_outflows = sum(outflows.values())

        return CashFlowResults(
            inflows=inflows,
            outflows=outflows,
            net_inflows=net_inflows,
            net_outflows=net_outflows,
            total_net_flow=net_inflows - net_outflows
        )

    def process_retirement_income(
        self,
        year: int,
        base_facts: BaseFacts
    ) -> IncomeResults:
        """Calculates all retirement income for the year."""
        income_streams = {}

        if year < base_facts.retirement_year:
            return IncomeResults(
                income_streams={},
                total_income=Decimal('0')
            )

        for income in base_facts.retirement_income:
            if not self._is_income_active(income, year):
                continue

            amount = to_decimal(income.annual_income)

            if income.apply_inflation:
                years_from_start = year - base_facts.start_year
                amount = apply_annual_inflation(
                    amount,
                    to_decimal(base_facts.base_assumptions.inflation_rate),
                    years_from_start
                )

            income_streams[income.income_plan_id] = amount

        return IncomeResults(
            income_streams=income_streams,
            total_income=sum(income_streams.values())
        )

    def generate_projection(
        self,
        base_facts: BaseFacts
    ) -> List[YearlyCalculationResult]:
        """Generates complete projection timeline."""
        self.validate_inputs(base_facts)

        results = []
        prior_result = None

        for year in range(base_facts.start_year, base_facts.end_year + 1):
            result = self.calculate_year(year, base_facts, prior_result)
            results.append(result)
            prior_result = result

        return results

    def validate_inputs(self, base_facts: BaseFacts) -> None:
        """Validates all inputs before calculation sequence begins."""
        if not base_facts.assets and not base_facts.liabilities:
            raise ValueError("Must have at least one asset or liability")

        if base_facts.start_year >= base_facts.retirement_year:
            raise ValueError("Start year must be before retirement year")

        if base_facts.retirement_year >= base_facts.end_year:
            raise ValueError("Retirement year must be before end year")

        for asset in base_facts.assets:
            if asset.value <= 0:
                raise ValueError(f"Asset {asset.asset_id} has invalid value")

        for liability in base_facts.liabilities:
            if liability.value <= 0:
                raise ValueError(f"Liability {liability.liability_id} has invalid value")

    def _carry_forward_values(
        self,
        prior_result: YearlyCalculationResult
    ) -> PortfolioValues:
        """Propagates prior year values forward."""
        return PortfolioValues(
            asset_values=prior_result.ending_portfolio.asset_values.copy(),
            liability_values=prior_result.ending_portfolio.liability_values.copy(),
            asset_category_totals=prior_result.ending_portfolio.asset_category_totals.copy(),
            liability_category_totals=prior_result.ending_portfolio.liability_category_totals.copy(),
            retirement_portfolio_value=prior_result.ending_portfolio.retirement_portfolio_value,
            total_net_worth=prior_result.ending_portfolio.total_net_worth
        )

    def _initialize_starting_values(self, base_facts: BaseFacts) -> PortfolioValues:
        """Creates initial portfolio state."""
        asset_values = {
            asset.asset_id: to_decimal(asset.value)
            for asset in base_facts.assets
        }

        liability_values = {
            liability.liability_id: to_decimal(liability.value)
            for liability in base_facts.liabilities
        }

        portfolio = PortfolioValues(
            asset_values=asset_values,
            liability_values=liability_values,
            asset_category_totals={},
            liability_category_totals={},
            retirement_portfolio_value=Decimal('0'),
            total_net_worth=Decimal('0')
        )

        return self._update_portfolio_totals(portfolio, base_facts)

    def _apply_flows_to_portfolio(
        self,
        portfolio: PortfolioValues,
        cash_flows: CashFlowResults,
        income: IncomeResults,
        base_facts: BaseFacts
    ) -> PortfolioValues:
        """Applies all cash movements to portfolio values."""
        # Calculate nest egg eligible flows
        nest_egg_inflows = sum(
            amount for flow_id, amount in cash_flows.inflows.items()
            if next(f for f in base_facts.inflows_outflows 
                if f.inflow_outflow_id == flow_id).include_in_nest_egg
        )
        
        nest_egg_outflows = sum(
            amount for flow_id, amount in cash_flows.outflows.items()
            if next(f for f in base_facts.inflows_outflows 
                if f.inflow_outflow_id == flow_id).include_in_nest_egg
        )

        # Apply flows to retirement portfolio if they're nest egg eligible
        nest_egg_net_flow = nest_egg_inflows - nest_egg_outflows
        portfolio.retirement_portfolio_value += nest_egg_net_flow + income.total_income

        return self._update_portfolio_totals(portfolio, base_facts)

    def _is_income_active(
        self,
        income: RetirementIncomePlan,
        year: int
    ) -> bool:
        """Determines if income is active for the year."""
        return income.start_year <= year <= (income.end_year or income.start_year)

    def _generate_calculation_metadata(
        self,
        year: int,
        portfolio: PortfolioValues,
        flows: CashFlowResults
    ) -> Dict:
        """Creates metadata about calculation process."""
        return {
            'year': year,
            'total_inflows': flows.net_inflows,
            'total_outflows': flows.net_outflows,
            'ending_portfolio_value': portfolio.retirement_portfolio_value
        }
