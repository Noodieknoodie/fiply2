# backend/database_operations/calculations/base_facts/inflows_outflows.py

"""Inflow and outflow calculation module for base facts.

This module handles cash flow calculations using a year-based approach.
Following the principle of "store what you know, calculate what you need":
- Cash flows are stored with start_year and optional end_year
- All calculations occur at the start of each year
- Inflation is applied before other adjustments
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, TypedDict, Literal
from enum import Enum

from ...utils.money_utils import to_decimal, to_float, apply_annual_inflation


class FlowType(str, Enum):
    """Enum for flow types."""
    INFLOW = "inflow"
    OUTFLOW = "outflow"


@dataclass
class CashFlowFact:
    """Represents an inflow or outflow with its core attributes.
    
    All monetary values are stored as float but converted to Decimal for calculations.
    Years are stored as integers, representing the full year (e.g., 2024).
    """
    annual_amount: float
    type: FlowType
    name: str
    start_year: int
    end_year: Optional[int]
    apply_inflation: bool

    @classmethod
    def from_db_row(cls, row: Dict) -> 'CashFlowFact':
        """Create a CashFlowFact from a database row dictionary."""
        return cls(
            annual_amount=float(row['annual_amount']),
            type=FlowType(row['type'].lower()),
            name=row['name'],
            start_year=int(row['start_year']),
            end_year=int(row['end_year']) if row.get('end_year') is not None else None,
            apply_inflation=bool(row['apply_inflation'])
        )


class CashFlowValueResult(TypedDict):
    """Type definition for cash flow calculation results."""
    name: str
    type: str
    annual_amount: float
    adjusted_amount: float
    is_active: bool
    inflation_applied: bool


def calculate_cash_flow_value(
    cash_flow: CashFlowFact,
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> CashFlowValueResult:
    """Calculate the value of a cash flow for a specific year.
    
    A cash flow is active if:
    - The calculation year is >= start_year
    - AND either there is no end_year OR the calculation year is <= end_year
    
    All calculations occur at the start of the year in this sequence:
    1. Check if flow is active
    2. Apply inflation if applicable
    
    Args:
        cash_flow: The cash flow to calculate
        calculation_year: The year to calculate the value for
        inflation_rate: Annual inflation rate for inflation-adjusted flows
        base_year: Starting year for inflation calculations (defaults to start_year)
        
    Returns:
        Dictionary containing the flow details and calculated values
    """
    # Convert values to Decimal for precise calculations
    annual_amount = to_decimal(cash_flow.annual_amount)
    
    # Check if flow is active in this year
    is_active = (
        calculation_year >= cash_flow.start_year and
        (cash_flow.end_year is None or calculation_year <= cash_flow.end_year)
    )
    
    if not is_active:
        return {
            'name': cash_flow.name,
            'type': cash_flow.type.value,
            'annual_amount': to_float(annual_amount),
            'adjusted_amount': 0.0,
            'is_active': False,
            'inflation_applied': False
        }
    
    # Calculate inflation adjustment if applicable
    adjusted_amount = annual_amount
    inflation_applied = False
    
    if cash_flow.apply_inflation and inflation_rate > 0:
        # If no base_year provided, use start_year
        base_year = base_year if base_year is not None else cash_flow.start_year
        years_of_inflation = calculation_year - base_year
        
        if years_of_inflation > 0:
            inflation_rate_decimal = to_decimal(str(inflation_rate))
            for _ in range(years_of_inflation):
                adjusted_amount = apply_annual_inflation(adjusted_amount, inflation_rate_decimal)
            inflation_applied = True
    
    return {
        'name': cash_flow.name,
        'type': cash_flow.type.value,
        'annual_amount': to_float(annual_amount),
        'adjusted_amount': to_float(adjusted_amount),
        'is_active': True,
        'inflation_applied': inflation_applied
    }


def aggregate_flows_by_type(
    cash_flows: List[CashFlowFact],
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> Dict[str, List[CashFlowValueResult]]:
    """Group and calculate cash flows by type for a specific year.
    
    Args:
        cash_flows: List of cash flows to aggregate
        calculation_year: Year to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted flows
        base_year: Starting year for inflation calculations
        
    Returns:
        Dictionary mapping flow types to lists of calculated values
    """
    results: Dict[str, List[CashFlowValueResult]] = {
        FlowType.INFLOW.value: [],
        FlowType.OUTFLOW.value: []
    }
    
    for flow in cash_flows:
        value = calculate_cash_flow_value(
            flow,
            calculation_year,
            inflation_rate,
            base_year
        )
        results[flow.type.value].append(value)
    
    return results


class TotalCashFlowsResult(TypedDict):
    """Type definition for total cash flows calculation results."""
    total_inflows: float
    total_outflows: float
    net_cash_flow: float
    metadata: Dict[str, Dict[Literal['total', 'active'], int]]


def calculate_total_cash_flows(
    cash_flows: List[CashFlowFact],
    calculation_year: int,
    inflation_rate: float = 0.0,
    base_year: int = None
) -> TotalCashFlowsResult:
    """Calculate total and net cash flow values for a specific year.
    
    Args:
        cash_flows: List of cash flows to total
        calculation_year: Year to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted flows
        base_year: Starting year for inflation calculations
        
    Returns:
        Dictionary containing inflow, outflow, and net totals, plus metadata
    """
    aggregated = aggregate_flows_by_type(
        cash_flows,
        calculation_year,
        inflation_rate,
        base_year
    )
    
    # Initialize totals as Decimal
    total_inflows = to_decimal('0')
    total_outflows = to_decimal('0')
    
    # Add up totals for each flow type
    if aggregated[FlowType.INFLOW.value]:
        total_inflows = sum(
            to_decimal(str(flow['adjusted_amount']))
            for flow in aggregated[FlowType.INFLOW.value]
        )
    
    if aggregated[FlowType.OUTFLOW.value]:
        total_outflows = sum(
            to_decimal(str(flow['adjusted_amount']))
            for flow in aggregated[FlowType.OUTFLOW.value]
        )
    
    # Calculate active counts
    active_inflows = sum(1 for flow in aggregated[FlowType.INFLOW.value] if flow['is_active'])
    active_outflows = sum(1 for flow in aggregated[FlowType.OUTFLOW.value] if flow['is_active'])
    
    return {
        'total_inflows': to_float(total_inflows),
        'total_outflows': to_float(total_outflows),
        'net_cash_flow': to_float(total_inflows - total_outflows),
        'metadata': {
            'inflows': {
                'total': len(aggregated[FlowType.INFLOW.value]),
                'active': active_inflows
            },
            'outflows': {
                'total': len(aggregated[FlowType.OUTFLOW.value]),
                'active': active_outflows
            }
        }
    } 