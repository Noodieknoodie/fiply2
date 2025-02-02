"""
Handles calculations for discrete event cash flows.
Follows core principles:
- Annual periods only
- No intra-year calculations
- Optional inflation adjustment
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from enum import Enum
from ...models import InflowOutflow
from ...utils.money_utils import to_decimal, apply_annual_inflation

class FlowType(Enum):
    """Flow type enumeration."""
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'

@dataclass
class CashFlowFact:
    """Represents a discrete event cash flow."""
    flow_id: int
    name: str
    flow_type: FlowType
    annual_amount: Decimal
    start_year: int
    end_year: int  # Same as start_year for single-year events
    apply_inflation: bool
    owner: str

@dataclass
class CashFlowCalculationResult:
    """Results of a cash flow calculation."""
    flow_id: int
    flow_name: str
    flow_type: FlowType
    base_amount: Decimal
    adjusted_amount: Decimal
    is_active: bool
    metadata: Dict

@dataclass
class AggregatedFlows:
    total_inflows: Decimal
    total_outflows: Decimal
    inflation_adjusted_inflows: Decimal
    inflation_adjusted_outflows: Decimal
    net_flow: Decimal

class CashFlowCalculator:
    """Handles cash flow calculations."""
    
    def calculate_flow_amount(
        self,
        flow: CashFlowFact,
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> CashFlowCalculationResult:
        """
        Calculate cash flow amount for a specific year.
        
        Args:
            flow: Cash flow to calculate
            year: Year to calculate for
            inflation_rate: Current inflation rate
            plan_start_year: Year the plan starts
            
        Returns:
            Calculation result including base and adjusted amounts
        """
        is_active = self._is_flow_active(flow, year)
        
        if not is_active:
            return CashFlowCalculationResult(
                flow_id=flow.flow_id,
                flow_name=flow.name,
                flow_type=flow.flow_type,
                base_amount=Decimal('0'),
                adjusted_amount=Decimal('0'),
                is_active=False,
                metadata=self._generate_metadata(flow, year)
            )

        base_amount = flow.annual_amount
        adjusted_amount = base_amount

        if flow.apply_inflation:
            years_from_start = year - plan_start_year
            adjusted_amount = apply_annual_inflation(base_amount, inflation_rate)

        return CashFlowCalculationResult(
            flow_id=flow.flow_id,
            flow_name=flow.name,
            flow_type=flow.flow_type,
            base_amount=base_amount,
            adjusted_amount=adjusted_amount,
            is_active=True,
            metadata=self._generate_metadata(flow, year)
        )

    def calculate_multiple_flows(
        self,
        flows: List[CashFlowFact],
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> List[CashFlowCalculationResult]:
        return [
            self.calculate_flow_amount(flow, year, inflation_rate, plan_start_year)
            for flow in flows
        ]

    def aggregate_flows(
        self,
        results: List[CashFlowCalculationResult]
    ) -> AggregatedFlows:
        inflows = Decimal('0')
        outflows = Decimal('0')
        adj_inflows = Decimal('0')
        adj_outflows = Decimal('0')
        for result in results:
            if not result.is_active:
                continue
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

    def _is_flow_active(self, flow: CashFlowFact, year: int) -> bool:
        """Check if flow is active in given year."""
        return flow.start_year <= year <= flow.end_year

    def _generate_metadata(self, flow: CashFlowFact, year: int) -> Dict:
        """Generate metadata for calculation result."""
        return {
            'flow_name': flow.name,
            'flow_type': flow.flow_type.value,
            'owner': flow.owner,
            'year': year,
            'is_single_year': flow.start_year == flow.end_year
        }

    def validate_cash_flows(
        self,
        flows: List[CashFlowFact]
    ) -> None:
        for flow in flows:
            if flow.annual_amount <= 0:
                raise ValueError(
                    f"Cash flow {flow.flow_id} has invalid amount"
                )
            if flow.end_year is not None and flow.start_year > flow.end_year:
                raise ValueError(
                    f"Cash flow {flow.flow_id} has invalid year sequence"
                )

    def calculate_total_flow_amount(
        self,
        annual_amount: Decimal,
        start_year: int,
        end_year: Optional[int],
        inflation_rate: Optional[Decimal] = None,
        apply_inflation: bool = False
    ) -> Decimal:
        actual_end = end_year or start_year
        duration = actual_end - start_year + 1
        if not apply_inflation or not inflation_rate:
            return annual_amount * duration
        total = Decimal('0')
        for year in range(duration):
            adjusted = apply_annual_inflation(
                annual_amount,
                inflation_rate,
                year
            )
            total += adjusted
        return total

    def calculate_total_inflation_impact(
        self,
        results: List[CashFlowCalculationResult]
    ) -> Dict[FlowType, Decimal]:
        impact = {
            FlowType.INFLOW: Decimal('0'),
            FlowType.OUTFLOW: Decimal('0')
        }
        for result in results:
            if result.is_active:
                impact[result.flow_type] += result.adjusted_amount - result.base_amount
        return impact

    def categorize_flows(
        self,
        flows: List[Tuple[FlowType, Decimal, str]]
    ) -> Dict[str, List[Tuple[FlowType, Decimal]]]:
        categories = {}
        for flow_type, amount, category in flows:
            if category not in categories:
                categories[category] = []
            categories[category].append((flow_type, amount))
        return categories
