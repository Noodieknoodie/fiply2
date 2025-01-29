"""Tests for base facts asset calculations."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from ...models import Asset, Plan
from ...calculations.base_facts.assets import (
    AssetFact,
    calculate_asset_value,
    aggregate_assets_by_category,
    calculate_total_assets
)
from ...calculations.base_facts import OwnerType, GrowthType
from .helpers import create_growth_config

# Test Data
SAMPLE_ASSETS = [
    {
        'value': 750000.0,
        'owner': 'Joint',
        'include_in_nest_egg': 0,
        'asset_category_id': 1,
        'asset_name': 'Primary Residence'
    },
    {
        'value': 500000.0,
        'owner': 'Person 1',
        'include_in_nest_egg': 1,
        'asset_category_id': 2,
        'asset_name': '401(k)'
    },
    {
        'value': 350000.0,
        'owner': 'Person 2',
        'include_in_nest_egg': 1,
        'asset_category_id': 2,
        'asset_name': 'IRA'
    }
]

@pytest.fixture
def sample_asset():
    """Create a sample asset for testing."""
    return AssetFact.from_db_row(SAMPLE_ASSETS[1])  # Using 401(k) as default test asset

@pytest.fixture
def real_assets(db_session):
    """Load real assets from Test Household A (plan_id=1)."""
    stmt = select(Asset).join(Plan).filter(Plan.plan_id == 1)
    assets = db_session.execute(stmt).scalars().all()
    
    return [AssetFact.from_db_row({
        'value': asset.value,
        'owner': asset.owner,
        'include_in_nest_egg': asset.include_in_nest_egg,
        'asset_category_id': asset.asset_category_id,
        'asset_name': asset.asset_name
    }) for asset in assets]

def calculate_expected_growth(principal: float, rate: float, years: float) -> float:
    """Helper function to calculate expected growth values using Decimal."""
    p = Decimal(str(principal))
    r = Decimal(str(rate))
    y = Decimal(str(years))
    result = p * (Decimal('1') + r) ** y
    return float(result.quantize(Decimal('0.01')))

def test_asset_fact_creation():
    """Test creation of AssetFact from database row."""
    asset = AssetFact.from_db_row(SAMPLE_ASSETS[0])
    assert asset.value == 750000.0
    assert asset.owner == OwnerType.JOINT
    assert asset.include_in_nest_egg == False
    assert asset.category_id == 1
    assert asset.name == 'Primary Residence'

def test_calculate_asset_value_no_growth(sample_asset):
    """Test asset value calculation without growth."""
    result = calculate_asset_value(sample_asset, date.today())
    assert result['current_value'] == 500000.0
    assert result['projected_value'] is None
    assert result['growth_applied'] is None
    assert result['included_in_totals'] == True

def test_calculate_asset_value_with_growth(sample_asset):
    """Test asset value calculation with growth configuration."""
    base_date = date(2025, 1, 1)
    sample_asset.growth_config = create_growth_config(
        rate=0.07,
        start_date=base_date,
        end_date=base_date + timedelta(days=365)
    )
    
    result = calculate_asset_value(sample_asset, base_date + timedelta(days=365))
    expected = calculate_expected_growth(500000.0, 0.07, 1.0)
    
    assert result['current_value'] == 500000.0
    assert result['projected_value'] is not None
    assert abs(result['projected_value'] - expected) < 0.01
    assert result['growth_applied'] == 0.07

def test_calculate_asset_value_with_stepwise_growth(sample_asset):
    """Test asset value calculation with stepwise growth configuration."""
    base_date = date(2025, 1, 1)
    
    sample_asset.growth_config = create_growth_config(
        rate=0.08,
        config_type=GrowthType.STEPWISE,
        start_date=base_date,
        end_date=base_date + timedelta(days=365 * 2)
    )
    
    # At 1 year
    result = calculate_asset_value(sample_asset, base_date + timedelta(days=365))
    expected_1_year = calculate_expected_growth(500000.0, 0.08, 1.0)
    assert abs(result['projected_value'] - expected_1_year) < 0.01
    
    # At 6 months
    result = calculate_asset_value(sample_asset, base_date + timedelta(days=182))
    expected_6_month = calculate_expected_growth(500000.0, 0.08, 182/365)
    assert abs(result['projected_value'] - expected_6_month) < 0.01
    
    # At 2 years
    result = calculate_asset_value(sample_asset, base_date + timedelta(days=365 * 2))
    expected_2_year = calculate_expected_growth(500000.0, 0.08, 2.0)
    assert abs(result['projected_value'] - expected_2_year) < 0.01
    
    # At 2.5 years with default rate
    result = calculate_asset_value(
        sample_asset,
        base_date + timedelta(days=int(365 * 2.5)),
        default_growth_rate=0.05
    )
    
    # Calculate in two steps using helper
    value_after_stepwise = calculate_expected_growth(500000.0, 0.08, 2.0)
    expected_final = calculate_expected_growth(value_after_stepwise, 0.05, 0.5)
    assert abs(result['projected_value'] - expected_final) < 0.01

def test_calculate_asset_value_with_stepwise_growth_no_default(sample_asset):
    """Test stepwise growth with no default rate after period."""
    base_date = date(2025, 1, 1)
    
    sample_asset.growth_config = create_growth_config(
        rate=0.08,
        config_type=GrowthType.STEPWISE,
        start_date=base_date,
        end_date=base_date + timedelta(days=365 * 2)
    )
    
    result = calculate_asset_value(
        sample_asset,
        base_date + timedelta(days=365 * 3)
    )
    
    expected = calculate_expected_growth(500000.0, 0.08, 2.0)
    assert abs(result['projected_value'] - expected) < 0.01

def test_aggregate_assets_by_category():
    """Test grouping and calculating assets by category."""
    assets = [AssetFact.from_db_row(row) for row in SAMPLE_ASSETS]
    results = aggregate_assets_by_category(assets, date(2025, 1, 1))
    
    assert len(results) == 2
    assert 1 in results
    assert 2 in results
    assert len(results[2]) == 2
    
    category_2_total = sum(r['current_value'] for r in results[2])
    assert abs(category_2_total - 850000.0) < 0.01

def test_calculate_total_assets():
    """Test calculation of total asset value."""
    assets = [AssetFact.from_db_row(row) for row in SAMPLE_ASSETS]
    result = calculate_total_assets(assets, date(2025, 1, 1))
    
    assert abs(result['current_value'] - 850000.0) < 0.01
    assert result['metadata']['asset_count'] == 3
    assert result['metadata']['included_count'] == 2

def test_real_data_asset_calculations(real_assets):
    """Test calculations with real data from the database."""
    calculation_date = date(2025, 1, 1)
    result = calculate_total_assets(real_assets, calculation_date)
    
    # Sum the values directly, convert to Decimal at the end
    expected_total = sum(
        asset.value for asset in real_assets 
        if asset.include_in_nest_egg
    )
    expected_total = Decimal(str(expected_total)).quantize(Decimal('0.01'))
    
    assert abs(result['current_value'] - float(expected_total)) < 0.01
def test_real_data_category_aggregation(real_assets):
    """Test category aggregation with real data."""
    calculation_date = date(2025, 1, 1)
    results = aggregate_assets_by_category(real_assets, calculation_date)
    
    categories = {asset.category_id for asset in real_assets}
    assert set(results.keys()) == categories
    
    for category_id in categories:
        category_assets = [a for a in real_assets if a.category_id == category_id]
        category_total = float(sum(
            Decimal(str(r['current_value'])) for r in results[category_id]
        ).quantize(Decimal('0.01')))
        expected_total = float(sum(
            Decimal(str(a.value)) for a in category_assets
        ).quantize(Decimal('0.01')))
        assert abs(category_total - expected_total) < 0.01