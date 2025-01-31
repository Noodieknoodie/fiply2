@dataclass
class CashFlowFact:
    """Represents inflow or outflow with amount, years, and inflation toggle."""

@dataclass
class CashFlowCalculationResult:
    """Results container tracking adjusted amounts and inflation impacts."""


class CashFlowCalculator:
    def calculate_flow_amount(self, flow: CashFlowFact, year: int, inflation_rate: Decimal) -> CashFlowCalculationResult:
        """Calculates flow amount for year, applying inflation if enabled."""

    def aggregate_flows_by_type(self, flows: List[CashFlowFact], year: int, inflation_rate: Decimal) -> Dict[str, Decimal]:
        """Groups and totals inflows and outflows separately."""

    def calculate_net_cash_flow(self, flows: List[CashFlowFact], year: int, inflation_rate: Decimal) -> Decimal:
        """Calculates net impact of all flows for the year."""

    def validate_cash_flows(self, flows: List[CashFlowFact]) -> None:
        """Validates flow inputs before calculations."""
