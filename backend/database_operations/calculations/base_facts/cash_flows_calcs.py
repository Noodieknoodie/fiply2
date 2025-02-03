"""
Handles calculations for discrete event cash flows.
Follows core principles:
- Annual periods only
- No intra-year calculations
- Optional inflation adjustment
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional
from enum import Enum

from ...utils.money_utils import to_decimal, apply_annual_inflation


class FlowType(Enum):
    """Represents cash flow types."""
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'


@dataclass
class CashFlowFact:
    """Defines a discrete cash flow event."""
    flow_id: int
    name: str
    flow_type: FlowType
    annual_amount: Decimal
    start_year: int
    end_year: int
    apply_inflation: bool
    owner: str


@dataclass
class CashFlowCalculationResult:
    """Stores results of cash flow calculations."""
    flow_id: int
    flow_name: str
    flow_type: FlowType
    base_amount: Decimal
    adjusted_amount: Decimal
    is_active: bool
    metadata: Dict


@dataclass
class AggregatedFlows:
    """Aggregates inflows and outflows, including inflation-adjusted values."""
    total_inflows: Decimal
    total_outflows: Decimal
    inflation_adjusted_inflows: Decimal
    inflation_adjusted_outflows: Decimal
    net_flow: Decimal


class CashFlowCalculator:
    """Handles cash flow calculations and aggregation."""

    def calculate_flow_amount(self, flow: CashFlowFact, year: int,
                              inflation_rate: Decimal, plan_start_year: int) -> CashFlowCalculationResult:
        """Computes cash flow for a given year."""
        is_active = flow.start_year <= year <= flow.end_year
        base_amount = flow.annual_amount if is_active else Decimal('0')
        adjusted_amount = apply_annual_inflation(base_amount, inflation_rate, year - plan_start_year) \
            if is_active and flow.apply_inflation else base_amount

        return CashFlowCalculationResult(
            flow_id=flow.flow_id,
            flow_name=flow.name,
            flow_type=flow.flow_type,
            base_amount=base_amount,
            adjusted_amount=adjusted_amount,
            is_active=is_active,
            metadata=self._generate_metadata(flow, year)
        )

    def calculate_multiple_flows(self, flows: List[CashFlowFact], year: int,
                                 inflation_rate: Decimal, plan_start_year: int) -> List[CashFlowCalculationResult]:
        """Computes cash flows for multiple events."""
        return [self.calculate_flow_amount(flow, year, inflation_rate, plan_start_year) for flow in flows]

    def aggregate_flows(self, results: List[CashFlowCalculationResult]) -> AggregatedFlows:
        """Aggregates inflows, outflows, and net cash flow."""
        inflows, outflows, adj_inflows, adj_outflows = Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0')
        for result in results:
            if result.is_active:
                if result.flow_type == FlowType.INFLOW:
                    inflows += result.base_amount
                    adj_inflows += result.adjusted_amount
                else:
                    outflows += result.base_amount
                    adj_outflows += result.adjusted_amount
        return AggregatedFlows(
            total_inflows=inflows,
            total_outflows=outflows,
            inflation_adjusted_inflows=adj_inflows,
            inflation_adjusted_outflows=adj_outflows,
            net_flow=adj_inflows - adj_outflows
        )

    def validate_cash_flows(self, flows: List[CashFlowFact]) -> None:
        """Ensures all cash flows have valid amounts and timelines."""
        for flow in flows:
            if flow.annual_amount <= 0:
                raise ValueError(f"Cash flow {flow.flow_id} has invalid amount.")
            if flow.start_year > flow.end_year:
                raise ValueError(f"Cash flow {flow.flow_id} has an invalid year sequence.")

    def calculate_total_flow_amount(self, annual_amount: Decimal, start_year: int, end_year: Optional[int],
                                    inflation_rate: Optional[Decimal] = None, apply_inflation: bool = False) -> Decimal:
        """Computes total cash flow over a period, optionally applying inflation."""
        duration = (end_year or start_year) - start_year + 1
        if not apply_inflation or not inflation_rate:
            return annual_amount * duration
        return sum(apply_annual_inflation(annual_amount, inflation_rate, year) for year in range(duration))

    def calculate_total_inflation_impact(self, results: List[CashFlowCalculationResult]) -> Dict[FlowType, Decimal]:
        """Computes the total impact of inflation on cash flows."""
        impact = {FlowType.INFLOW: Decimal('0'), FlowType.OUTFLOW: Decimal('0')}
        for result in results:
            if result.is_active:
                impact[result.flow_type] += result.adjusted_amount - result.base_amount
        return impact

    def _generate_metadata(self, flow: CashFlowFact, year: int) -> Dict:
        """Creates metadata for a cash flow calculation."""
        return {
            "flow_name": flow.name,
            "flow_type": flow.flow_type.value,
            "owner": flow.owner,
            "year": year,
            "is_single_year": flow.start_year == flow.end_year
        }

