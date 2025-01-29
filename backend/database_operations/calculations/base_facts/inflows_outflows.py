# backend/database_operations/calculations/base_facts/inflows_outflows.py

"""Inflow and outflow calculation module for base facts."""
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, TypedDict, Literal
from enum import Enum

from ...utils.date_utils import is_date_range_active
from ...utils.money_utils import to_decimal, to_float

class FlowType(str, Enum):
    """Enum for flow types."""
    INFLOW = "inflow"
    OUTFLOW = "outflow"

@dataclass
class CashFlowFact:
    """Represents an inflow or outflow with its core attributes."""
    annual_amount: float
    type: FlowType
    name: str
    start_date: date
    end_date: Optional[date]
    apply_inflation: bool

    @classmethod
    def from_db_row(cls, row: Dict) -> 'CashFlowFact':
        """Create a CashFlowFact from a database row dictionary."""
        return cls(
            annual_amount=float(row['annual_amount']),
            type=FlowType(row['type'].lower()),
            name=row['name'],
            start_date=row['start_date'],
            end_date=row['end_date'],
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
    calculation_date: date,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> CashFlowValueResult:
    """
    Calculate the value of a cash flow at a specific date.
    
    A cash flow is considered active if:
    - The calculation date is strictly after the start date (exclusive)
    - AND either there is no end date OR the calculation date is before the end date (exclusive)
    
    Following financial industry standard:
    - Cash flows start AFTER their start date
    - Cash flows end BEFORE their end date
    
    Args:
        cash_flow: The cash flow to calculate
        calculation_date: The date to calculate the value for
        inflation_rate: Annual inflation rate to apply if flow is inflation-adjusted
        base_date: The starting date for calculations
        
    Returns:
        Dictionary containing the flow details and calculated values
    """
    # Convert values to Decimal for precise calculations
    annual_amount = to_decimal(cash_flow.annual_amount)
    
    # Check if flow is active at calculation date
    # Following standard: start_date < calculation_date < end_date
    is_active = (
        cash_flow.start_date < calculation_date and
        (cash_flow.end_date is None or calculation_date < cash_flow.end_date)
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
        years = to_decimal((calculation_date - base_date).days) / to_decimal('365')
        inflation_factor = (to_decimal('1') + to_decimal(inflation_rate)) ** years
        adjusted_amount *= inflation_factor
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
    calculation_date: date,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> Dict[str, List[CashFlowValueResult]]:
    """
    Group and calculate cash flows by type (inflow/outflow).
    
    Args:
        cash_flows: List of cash flows to aggregate
        calculation_date: Date to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted flows
        base_date: Starting date for calculations
        
    Returns:
        Dictionary mapping flow types to lists of calculated values
    """
    results: Dict[str, List[CashFlowValueResult]] = {
        FlowType.INFLOW.value: [],
        FlowType.OUTFLOW.value: []
    }
    
    for flow in cash_flows:
        value = calculate_cash_flow_value(flow, calculation_date, inflation_rate, base_date)
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
    calculation_date: date,
    inflation_rate: float = 0.0,
    base_date: date = date.today()
) -> TotalCashFlowsResult:
    """
    Calculate total and net cash flow values.
    
    Args:
        cash_flows: List of cash flows to total
        calculation_date: Date to calculate values for
        inflation_rate: Annual inflation rate for inflation-adjusted flows
        base_date: Starting date for calculations
        
    Returns:
        Dictionary containing inflow, outflow, and net totals, plus metadata
    """
    aggregated = aggregate_flows_by_type(cash_flows, calculation_date, inflation_rate, base_date)
    
    # Initialize totals as Decimal
    total_inflows = to_decimal('0')
    total_outflows = to_decimal('0')
    
    # Add up totals if there are any flows
    if aggregated[FlowType.INFLOW.value]:
        total_inflows = sum(
            to_decimal(flow['adjusted_amount'])
            for flow in aggregated[FlowType.INFLOW.value]
        )
    
    if aggregated[FlowType.OUTFLOW.value]:
        total_outflows = sum(
            to_decimal(flow['adjusted_amount'])
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