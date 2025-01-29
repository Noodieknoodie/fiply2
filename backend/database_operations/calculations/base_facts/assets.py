# backend/database_operations/calculations/base_facts/assets.py 

"""Asset calculation module for financial planning."""

from datetime import date
from typing import List, Dict, Optional
from dataclasses import dataclass
from . import CalculationResult, GrowthConfig, TimeRange, GrowthType, OwnerType
from ...utils.money_utils import to_decimal, to_float

@dataclass
class AssetFact:
    """Represents an asset with its calculation parameters."""
    value: float
    owner: OwnerType
    include_in_nest_egg: bool
    category_id: int
    name: str
    growth_config: Optional[GrowthConfig] = None
    
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

def calculate_growth(
    principal: float,
    annual_rate: float,
    start_date: date,
    calculation_date: date,
    end_date: Optional[date] = None,
    growth_type: GrowthType = GrowthType.OVERRIDE,
    default_rate: Optional[float] = None
) -> float:
    """
    Calculate growth using simple compound interest.
    
    Following financial industry standard:
    - Growth applies ON the start_date (inclusive)
    - Growth applies UNTIL but not ON the end_date (exclusive)
    - Minimum of 1 day of growth when calculation_date equals start_date
    """
    # Standard: start_date <= calculation_date < end_date
    if calculation_date < start_date:
        return principal

    p = to_decimal(principal)
    r = to_decimal(annual_rate)
    
    if growth_type == GrowthType.STEPWISE and end_date:
        if calculation_date < end_date:  # Exclusive end
            # Within stepwise period - use stepwise rate
            # Minimum 1 day of growth when dates match
            days = max(to_decimal('1'), to_decimal((calculation_date - start_date).days))
            years = days / to_decimal('365')
            result = p * (to_decimal('1') + r) ** years
        else:
            # Past stepwise period:
            # 1. First calculate full stepwise growth to end date
            stepwise_years = to_decimal((end_date - start_date).days) / to_decimal('365')
            value_at_transition = p * (to_decimal('1') + r) ** stepwise_years
            
            # 2. Then apply default rate from end date forward
            if default_rate is not None:
                dr = to_decimal(default_rate)
                remaining_years = to_decimal((calculation_date - end_date).days) / to_decimal('365')
                result = value_at_transition * (to_decimal('1') + dr) ** remaining_years
            else:
                result = value_at_transition
    else:
        # Standard growth
        # Minimum 1 day of growth when dates match
        days = max(to_decimal('1'), to_decimal((calculation_date - start_date).days))
        years = days / to_decimal('365')
        result = p * (to_decimal('1') + r) ** years
    
    return to_float(result)

def calculate_asset_value(
    asset: AssetFact,
    calculation_date: date,
    scenario_id: Optional[int] = None,
    default_growth_rate: Optional[float] = None
) -> CalculationResult:
    """Calculate the current and projected value of an asset."""
    current_value = asset.value
    projected_value = current_value
    applied_rate = None
    
    result: CalculationResult = {
        'current_value': current_value,
        'projected_value': None,
        'growth_applied': None,
        'included_in_totals': asset.include_in_nest_egg,
        'metadata': {
            'name': asset.name,
            'category_id': asset.category_id,
            'owner': asset.owner.value
        }
    }
    
    if asset.growth_config:
        growth = asset.growth_config
        print(f"\nCalculating growth for {asset.name}:")
        print(f"Current Value: {current_value}")
        print(f"Growth Rate: {growth.rate}")
        print(f"Start Date: {growth.time_range.start_date}")
        print(f"Calc Date: {calculation_date}")
        
        start = (growth.time_range and growth.time_range.start_date) or calculation_date
        end = growth.time_range.end_date if growth.time_range else None
        
        projected_value = calculate_growth(
            principal=current_value,
            annual_rate=growth.rate,
            start_date=start,
            calculation_date=calculation_date,
            end_date=end,
            growth_type=growth.config_type,
            default_rate=default_growth_rate
        )
        print(f"Projected Value: {projected_value}")
        applied_rate = growth.rate
    
    # Set projected value if there's any meaningful growth
    result['projected_value'] = projected_value if abs(projected_value - current_value) > 0.01 else None
    result['growth_applied'] = applied_rate
    
    return result

def aggregate_assets_by_category(
    assets: List[AssetFact],
    calculation_date: date,
    scenario_id: Optional[int] = None
) -> Dict[int, List[CalculationResult]]:
    """Group and calculate assets by category."""
    results: Dict[int, List[CalculationResult]] = {}
    
    for asset in assets:
        result = calculate_asset_value(asset, calculation_date, scenario_id)
        if asset.category_id not in results:
            results[asset.category_id] = []
        results[asset.category_id].append(result)
    
    return results

def calculate_total_assets(
    assets: List[AssetFact],
    calculation_date: date,
    scenario_id: Optional[int] = None
) -> CalculationResult:
    """Calculate the total value of all assets."""
    current_total = to_decimal('0')
    projected_total = to_decimal('0')
    included_count = 0
    
    for asset in assets:
        result = calculate_asset_value(asset, calculation_date, scenario_id)
        
        if result['included_in_totals']:
            current_total += to_decimal(result['current_value'])
            if result['projected_value'] is not None:
                projected_total += to_decimal(result['projected_value'])
            included_count += 1
    
    return {
        'current_value': to_float(current_total),
        'projected_value': to_float(projected_total) if projected_total > 0 else None,
        'growth_applied': None,
        'included_in_totals': True,
        'metadata': {
            'asset_count': len(assets),
            'included_count': included_count
        }
    }