@dataclass
class AssetFact:
    """Core asset data including value, growth configuration, and categorization."""

@dataclass
class GrowthConfig:
    """Growth rate configuration supporting default, override, and stepwise types."""

@dataclass
class AssetCalculationResult:
    """Results container for asset calculations including base and projected values."""


class AssetCalculator:
    def calculate_asset_value(self, asset: AssetFact, year: int, default_rate: Decimal) -> AssetCalculationResult:
        """Calculates asset value for a specific year applying appropriate growth."""

    def apply_growth_rate(self, value: Decimal, config: GrowthConfig, year: int, default_rate: Decimal) -> Decimal:
        """Applies growth following hierarchy: asset-specific, stepwise, then default."""

    def aggregate_by_category(self, assets: List[AssetFact], year: int) -> Dict[str, Decimal]:
        """Groups and totals assets by their categories."""

    def calculate_nest_egg_total(self, assets: List[AssetFact], year: int) -> Decimal:
        """Calculates total for assets included in retirement portfolio."""

    def validate_asset_facts(self, assets: List[AssetFact]) -> None:
        """Validates asset inputs before calculations."""
