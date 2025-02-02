"""
## Scheduled Inflows/Outflows
- Start year, end year (stored as entered but converted as needed)
- Amount
- Optional inflation toggle
- For discrete events only
- Input in years
- Examples: College (start year, end year different), inheritance (start year, end year the same)
## Annual Calculation Order
2. Apply scheduled inflows (inflation-adjusted if enabled)
3. Apply scheduled outflows (inflation-adjusted if enabled)
## Value Display Principles
- All values shown in current dollars
- Inflation adjustments compound annually
- No partial year or day counting
- No cash flow timing within year
- All events assumed to occur at year boundaries
Key features of this implementation:
1. Proper handling of single-year vs multi-year flows
2. Optional inflation adjustments
3. Clear separation of inflows and outflows
4. Support for owner-based tracking
5. Detailed metadata for flow analysis
6. Utilities for analyzing flows by duration
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional
from enum import Enum
from ...models import InflowOutflow
from ...utils.money_utils import to_decimal, apply_annual_inflation
class FlowType(Enum):
    # Enumeration of flow types.
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'
@dataclass
class CashFlowFact:
    """Represents scheduled inflow or outflow."""
    flow_id: int
    name: str
    flow_type: FlowType
    annual_amount: Decimal
    start_year: int
    end_year: Optional[int]  # None means same as start_year
    apply_inflation: bool
    owner: str
@dataclass
class CashFlowCalculationResult:
    """Results container for cash flow calculations."""
    flow_id: int
    flow_name: str
    flow_type: FlowType
    base_amount: Decimal
    adjusted_amount: Decimal
    inflation_adjustment: Decimal
    is_active: bool
    metadata: Dict
@dataclass
class AggregatedFlows:
    """Container for aggregated flow totals."""
    total_inflows: Decimal
    total_outflows: Decimal
    inflation_adjusted_inflows: Decimal
    inflation_adjusted_outflows: Decimal
    net_flow: Decimal
class CashFlowCalculator:
    """Handles scheduled inflow and outflow calculations."""
    def calculate_flow_amount(
        self,
        flow: CashFlowFact,
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> CashFlowCalculationResult:
        # Calculates cash flow amount for a specific year.
        # Args:
        #     flow: Cash flow data container
        #     year: Year to calculate for
        #     inflation_rate: Annual inflation rate
        #     plan_start_year: Year plan started (for inflation calculations)
        # Returns:
        #     Calculation results including base and adjusted amounts    
        # Determine if flow is active in this year
        is_active = self._is_flow_active(flow, year)
        if not is_active:
            return CashFlowCalculationResult(
                flow_id=flow.flow_id,
                flow_name=flow.name,
                flow_type=flow.flow_type,
                base_amount=flow.annual_amount,
                adjusted_amount=Decimal('0'),
                inflation_adjustment=Decimal('0'),
                is_active=False,
                metadata=self._generate_calculation_metadata(
                    flow, year, Decimal('0')
                )
            )
        # Start with base amount
        base_amount = flow.annual_amount
        adjusted_amount = base_amount
        inflation_adjustment = Decimal('0')
        # Apply inflation if enabled
        if flow.apply_inflation:
            years_from_start = year - plan_start_year
            adjusted_amount = apply_annual_inflation(
                base_amount,
                inflation_rate,
                years_from_start
            )
            inflation_adjustment = adjusted_amount - base_amount
        return CashFlowCalculationResult(
            flow_id=flow.flow_id,
            flow_name=flow.name,
            flow_type=flow.flow_type,
            base_amount=base_amount,
            adjusted_amount=adjusted_amount,
            inflation_adjustment=inflation_adjustment,
            is_active=True,
            metadata=self._generate_calculation_metadata(
                flow, year, inflation_adjustment
            )
        )
    def calculate_multiple_flows(
        self,
        flows: List[CashFlowFact],
        year: int,
        inflation_rate: Decimal,
        plan_start_year: int
    ) -> List[CashFlowCalculationResult]:
        # Calculates amounts for multiple cash flows.
        # Args:
        #     flows: List of cash flows to calculate
        #     year: Year to calculate for
        #     inflation_rate: Annual inflation rate
        #     plan_start_year: Year plan started
        # Returns:
        #     List of calculation results for each flow
        return [
            self.calculate_flow_amount(
                flow, year, inflation_rate, plan_start_year
            )
            for flow in flows
        ]
    def aggregate_flows(
        self,
        results: List[CashFlowCalculationResult]
    ) -> AggregatedFlows:
        # Aggregates inflows and outflows with inflation adjustments.
        # Args:
        #     results: List of cash flow calculation results
        # Returns:
        #     Aggregated totals for inflows and outflows
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
    def _is_flow_active(
        self,
        flow: CashFlowFact,
        year: int
    ) -> bool:
        """Determines if flow is active in the given year."""
        end_year = flow.end_year or flow.start_year
        return flow.start_year <= year <= end_year
    def _generate_calculation_metadata(
        self,
        flow: CashFlowFact,
        year: int,
        inflation_adjustment: Decimal
    ) -> Dict:
        """Creates metadata about calculation process."""
        return {
            'flow_name': flow.name,
            'flow_type': flow.flow_type.value,
            'owner': flow.owner,
            'year': year,
            'inflation_enabled': flow.apply_inflation,
            'inflation_adjustment': str(inflation_adjustment),
            'is_single_year': flow.end_year is None or flow.end_year == flow.start_year,
            'years_active': (flow.end_year or flow.start_year) - flow.start_year + 1
        }
    def validate_cash_flows(
        self,
        flows: List[CashFlowFact]
    ) -> None:
        """Validates cash flow inputs before calculations."""
        for flow in flows:
            # Validate amount is positive
            if flow.annual_amount <= 0:
                raise ValueError(
                    f"Cash flow {flow.flow_id} has invalid amount"
                )
            # Validate year sequence
            if flow.end_year is not None:
                if flow.start_year > flow.end_year:
                    raise ValueError(
                        f"Cash flow {flow.flow_id} has invalid year sequence"
                    )
    def get_single_year_flows(
        self,
        results: List[CashFlowCalculationResult]
    ) -> List[CashFlowCalculationResult]:
        # Returns list of single-year cash flows (like inheritances).
        return [
            r for r in results 
            if r.metadata['is_single_year']
        ]
    def get_multi_year_flows(
        self,
        results: List[CashFlowCalculationResult]
    ) -> List[CashFlowCalculationResult]:
        # Returns list of multi-year cash flows (like college expenses).
        return [
            r for r in results 
            if not r.metadata['is_single_year']
        ]
    def calculate_total_inflation_impact(
        self,
        results: List[CashFlowCalculationResult]
    ) -> Dict[FlowType, Decimal]:
        # Calculates total inflation impact by flow type.
        impact = {
            FlowType.INFLOW: Decimal('0'),
            FlowType.OUTFLOW: Decimal('0')
        }
        for result in results:
            if result.is_active:
                impact[result.flow_type] += result.inflation_adjustment
        return impact