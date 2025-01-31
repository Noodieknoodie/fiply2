# backend/database_operations/calculations/base_facts/assets.py 

"""Asset calculation module for base facts.

This module handles asset calculations using a year-based approach.
Following the principle of "store what you know, calculate what you need":
- Asset values are stored with their base value
- Growth configurations use explicit years (not dates)
- All calculations occur at the start of each year
"""

from typing import List, Dict, Optional, TypedDict, Literal
from dataclasses import dataclass
from decimal import Decimal
from . import GrowthType, OwnerType
from ...utils.money_utils import to_decimal, to_float

@dataclass
class GrowthPeriod:
    """Represents a growth period with explicit years.
    
    All years are stored as integers (e.g., 2025).
    Growth applies at the start of each year.
    """
    start_year: int
    end_year: Optional[int] = None
    rate: float = 0.0
    growth_type: GrowthType = GrowthType.OVERRIDE

@dataclass
class AssetFact:
    """Represents an asset with its core attributes.
    
    All monetary values are stored as float but converted to Decimal for calculations.
    Growth rates are stored as float but converted to Decimal for calculations.
    """
    value: float
    owner: OwnerType
    include_in_nest_egg: bool
    category_id: int
    name: str
    growth_config: Optional[GrowthPeriod] = None
    
    @classmethod
    def from_db_row(cls, row: Dict) -> 'AssetFact':
        """Create an AssetFact from a database row."""
        return cls(
            value=float(row['value']),
            owner=OwnerType(row['owner']),
            include_in_nest_egg=bool(row['include_in_nest_egg']),
            category_id=int(row['asset_category_id']),
            name=row['asset_name'],
            growth_config=None  # Will be set separately from growth_rate_configurations
        )

class AssetValueResult(TypedDict):
    """Type definition for asset value calculation results."""
    name: str
    owner: str
    base_value: float
    projected_value: float
    growth_applied: Optional[float]
    included_in_totals: bool
    metadata: Dict[str, str]

def calculate_growth(
    principal: float,
    annual_rate: float,
    calculation_year: int,
    start_year: int,
    end_year: Optional[int] = None,
    growth_type: GrowthType = GrowthType.OVERRIDE,
    default_rate: Optional[float] = None
) -> float:
    """Calculate growth using simple compound interest on a yearly basis.
    
    Following the SINGLE SOURCE OF TRUTH:
    1. Growth applies at the start of each year
    2. Growth compounds annually
    3. For stepwise growth, transitions occur at year boundaries
    
    Args:
        principal: Initial amount to grow
        annual_rate: Annual growth rate as decimal (e.g., 0.05 for 5%)
        calculation_year: Year to calculate value for
        start_year: Year growth begins
        end_year: Optional year growth pattern ends
        growth_type: Type of growth calculation
        default_rate: Default rate to use after stepwise period
    
    Returns:
        Grown value as float
    """
    if calculation_year < start_year:
        return principal

    p = to_decimal(principal)
    r = to_decimal(annual_rate)
    
    if growth_type == GrowthType.STEPWISE and end_year:
        if calculation_year <= end_year:
            # Within stepwise period - use stepwise rate
            years = calculation_year - start_year
            result = p * (to_decimal('1') + r) ** years
        else:
            # Past stepwise period:
            # 1. First calculate full stepwise growth to end year
            stepwise_years = end_year - start_year
            value_at_transition = p * (to_decimal('1') + r) ** stepwise_years
            
            # 2. Then apply default rate from end year forward
            if default_rate is not None:
                dr = to_decimal(default_rate)
                remaining_years = calculation_year - end_year
                result = value_at_transition * (to_decimal('1') + dr) ** remaining_years
            else:
                result = value_at_transition
    else:
        # Standard growth
        years = calculation_year - start_year
        result = p * (to_decimal('1') + r) ** years
    
    return to_float(result)

def calculate_asset_value(
    asset: AssetFact,
    calculation_year: int,
    base_year: Optional[int] = None,
    default_growth_rate: Optional[float] = None
) -> AssetValueResult:
    """Calculate the value of an asset for a specific year.
    
    Following the SINGLE SOURCE OF TRUTH:
    1. Base value is stored and never modified
    2. Growth applies at the start of each year
    3. Growth compounds annually
    
    Args:
        asset: The asset to calculate
        calculation_year: Year to calculate the value for
        base_year: Starting year for growth calculations
        default_growth_rate: Default growth rate if needed
        
    Returns:
        Dictionary containing the asset details and calculated values
    """
    base_value = to_decimal(asset.value)
    projected_value = base_value
    applied_rate = None
    
    if asset.growth_config and (base_year is not None):
        growth = asset.growth_config
        start_year = base_year
        end_year = None
        
        if isinstance(growth, GrowthPeriod):
            # Use explicit years from growth period
            start_year = growth.start_year
            end_year = growth.end_year
        
        projected_value = to_decimal(
            calculate_growth(
                principal=to_float(base_value),
                annual_rate=growth.rate,
                calculation_year=calculation_year,
                start_year=start_year,
                end_year=end_year,
                growth_type=growth.growth_type,
                default_rate=default_growth_rate
            )
        )
        applied_rate = growth.rate
    
    return {
        'name': asset.name,
        'owner': asset.owner.value,
        'base_value': to_float(base_value),
        'projected_value': to_float(projected_value),
        'growth_applied': applied_rate,
        'included_in_totals': asset.include_in_nest_egg,
        'metadata': {
            'category_id': str(asset.category_id)
        }
    }

def aggregate_assets_by_category(
    assets: List[AssetFact],
    calculation_year: int,
    base_year: Optional[int] = None,
    default_growth_rate: Optional[float] = None
) -> Dict[int, List[AssetValueResult]]:
    """Group and calculate assets by category for a specific year.
    
    Args:
        assets: List of assets to aggregate
        calculation_year: Year to calculate values for
        base_year: Starting year for growth calculations
        default_growth_rate: Default growth rate if needed
        
    Returns:
        Dictionary mapping category IDs to lists of calculated values
    """
    results: Dict[int, List[AssetValueResult]] = {}
    
    for asset in assets:
        result = calculate_asset_value(
            asset,
            calculation_year,
            base_year,
            default_growth_rate
        )
        if asset.category_id not in results:
            results[asset.category_id] = []
        results[asset.category_id].append(result)
    
    return results

class TotalAssetsResult(TypedDict):
    """Type definition for total assets calculation results."""
    total_base_value: float
    total_projected_value: float
    metadata: Dict[str, Dict[Literal['total', 'included'], int]]

def calculate_total_assets(
    assets: List[AssetFact],
    calculation_year: int,
    base_year: Optional[int] = None,
    default_growth_rate: Optional[float] = None
) -> TotalAssetsResult:
    """Calculate total asset values for a specific year.
    
    Args:
        assets: List of assets to total
        calculation_year: Year to calculate values for
        base_year: Starting year for growth calculations
        default_growth_rate: Default growth rate if needed
        
    Returns:
        Dictionary containing base and projected totals, plus metadata
    """
    total_base = to_decimal('0')
    total_projected = to_decimal('0')
    total_count = len(assets)
    included_count = 0
    
    for asset in assets:
        result = calculate_asset_value(
            asset,
            calculation_year,
            base_year,
            default_growth_rate
        )
        
        if result['included_in_totals']:
            total_base += to_decimal(result['base_value'])
            total_projected += to_decimal(result['projected_value'])
            included_count += 1
    
    return {
        'total_base_value': to_float(total_base),
        'total_projected_value': to_float(total_projected),
        'metadata': {
            'assets': {
                'total': total_count,
                'included': included_count
            }
        }
    }