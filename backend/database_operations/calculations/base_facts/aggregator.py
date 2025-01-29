"""Aggregator module for combining all base fact calculations into year-by-year projections."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, TypedDict, Any
from decimal import Decimal

from ...utils.money_utils import to_decimal, to_float
from ...utils.date_utils import is_date_range_active

from . import assets as asset_calc
from . import liabilities as liability_calc
from . import inflows_outflows as flow_calc
from . import retirement_income as retirement_calc

@dataclass
class BaseFactsInput:
    """Container for all base facts needed for projections."""
    assets: List[asset_calc.AssetFact]
    liabilities: List[liability_calc.LiabilityFact]
    cash_flows: List[flow_calc.CashFlowFact]
    retirement_income: List[retirement_calc.RetirementIncomeFact]
    default_growth_rate: float
    inflation_rate: float
    base_date: date
    final_date: date

class YearlyProjectionResult(TypedDict):
    """Type definition for yearly projection results."""
    year: int
    date: date
    assets: Dict[str, float]  # total_assets, nest_egg_assets
    liabilities: Dict[str, float]  # total_liabilities, nest_egg_liabilities
    cash_flows: Dict[str, float]  # total_inflows, total_outflows, net_cash_flow
    retirement_income: Dict[str, float]  # total_income, nest_egg_income
    net_worth: float
    retirement_portfolio: float  # Only includes nest egg components

def calculate_yearly_projection(
    base_facts: BaseFactsInput,
    calculation_date: date,
    scenario_id: Optional[int] = None
) -> YearlyProjectionResult:
    """
    Calculate financial projections for a specific year.
    """
    # Calculate individual asset values with growth
    asset_values = [
        asset_calc.calculate_asset_value(
            asset, 
            calculation_date, 
            scenario_id,
            default_growth_rate=base_facts.default_growth_rate
        )
        for asset in base_facts.assets
    ]

    # Calculate total and nest egg assets using projected values
    total_assets = sum(
        to_decimal(v['projected_value'] if v['projected_value'] is not None else v['current_value'])
        for v in asset_values
    ).quantize(Decimal('0.01'))

    nest_egg_assets = sum(
        to_decimal(v['projected_value'] if v['projected_value'] is not None else v['current_value'])
        for asset, v in zip(base_facts.assets, asset_values)
        if asset.include_in_nest_egg
    ).quantize(Decimal('0.01'))

    # Calculate individual liability values
    liability_values = [
        liability_calc.calculate_liability_value(
            liability,
            calculation_date,
            base_facts.base_date
        )
        for liability in base_facts.liabilities
    ]

    # Use the same pattern for liabilities
    total_liabilities = sum(
        to_decimal(v['projected_value'] if v['projected_value'] is not None else v['current_value'])
        for v in liability_values
    ).quantize(Decimal('0.01'))

    nest_egg_liabilities = sum(
        to_decimal(v['projected_value'] if v['projected_value'] is not None else v['current_value'])
        for liability, v in zip(base_facts.liabilities, liability_values)
        if liability.include_in_nest_egg
    ).quantize(Decimal('0.01'))

    # Rest of calculations remain the same
    cash_flow_totals = flow_calc.calculate_total_cash_flows(
        base_facts.cash_flows,
        calculation_date,
        base_facts.inflation_rate,
        base_facts.base_date
    )
    
    retirement_totals = retirement_calc.calculate_total_retirement_income(
        base_facts.retirement_income,
        calculation_date,
        base_facts.inflation_rate,
        base_facts.base_date
    )

    net_worth = to_float(total_assets - total_liabilities)
    retirement_portfolio = to_float(nest_egg_assets - nest_egg_liabilities)

    return {
        'year': calculation_date.year,
        'date': calculation_date,
        'assets': {
            'total_assets': to_float(total_assets),
            'nest_egg_assets': to_float(nest_egg_assets)
        },
        'liabilities': {
            'total_liabilities': to_float(total_liabilities),
            'nest_egg_liabilities': to_float(nest_egg_liabilities)
        },
        'cash_flows': {
            'total_inflows': cash_flow_totals['total_inflows'],
            'total_outflows': cash_flow_totals['total_outflows'],
            'net_cash_flow': cash_flow_totals['net_cash_flow']
        },
        'retirement_income': {
            'total_income': retirement_totals['total_income'],
            'nest_egg_income': retirement_totals['nest_egg_income']
        },
        'net_worth': net_worth,
        'retirement_portfolio': retirement_portfolio
    }

def generate_projection_timeline(
    base_facts: BaseFactsInput,
    scenario_id: Optional[int] = None
) -> List[YearlyProjectionResult]:
    """
    Generate year-by-year projections from base date to final date.
    
    Args:
        base_facts: Container with all base facts data
        scenario_id: Optional scenario ID for overrides
        
    Returns:
        List of yearly projections in chronological order
    """
    projections: List[YearlyProjectionResult] = []
    current_date = base_facts.base_date
    
    while current_date <= base_facts.final_date:
        yearly_result = calculate_yearly_projection(
            base_facts,
            current_date,
            scenario_id
        )
        projections.append(yearly_result)
        
        # Move to next year
        current_date = date(current_date.year + 1, current_date.month, current_date.day)
    
    return projections