# tests/test_growth_calculations.py
from decimal import Decimal
import pytest
from datetime import date
from database_operations.calculations.base_facts.growth_handler_calcs import GrowthRateHandler
from database_operations.models import GrowthRateConfiguration
from database_operations.utils.time_utils import get_year_for_age

def test_default_growth_application():
    """Test application of default growth rate."""
    handler = GrowthRateHandler()
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.06'),
        growth_configs=[]  # No configurations = use default
    )
    assert result.final_value == Decimal('106000')
    assert result.growth_amount == Decimal('6000')
    assert result.rate_source == 'default'

def test_stepwise_growth_handling():
    """Test stepwise growth rate application."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2027,
            growth_rate=Decimal('0.08')
        ),
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2028,
            end_year=2030,
            growth_rate=Decimal('0.06')
        )
    ]
    
    # Test first period
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.final_value == Decimal('108000')
    assert result.rate_source == 'stepwise'
    
    # Test gap year (should use default)
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2031,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'default'
    assert result.final_value == Decimal('105000')

def test_growth_rate_period_boundaries():
    """Test growth rate calculations at period boundaries."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2027,
            growth_rate=Decimal('0.08')
        )
    ]
    
    # Test exactly at start year
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'stepwise'
    assert result.final_value == Decimal('108000')
    
    # Test exactly at end year
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2027,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'stepwise'
    assert result.final_value == Decimal('108000')
    
    # Test one year before start
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2024,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'default'
    assert result.final_value == Decimal('105000')
    
    # Test one year after end
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2028,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'default'
    assert result.final_value == Decimal('105000')

def test_overlapping_growth_periods():
    """Test handling of overlapping growth period configurations."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2027,
            growth_rate=Decimal('0.08')
        ),
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2026,
            end_year=2028,
            growth_rate=Decimal('0.06')
        )
    ]
    
    # Test in overlap period (should use first configured rate)
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2026,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'stepwise'
    assert result.final_value == Decimal('108000')  # Uses first rate (0.08)

def test_growth_rate_transitions():
    """Test growth rate transitions between periods."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2026,
            growth_rate=Decimal('0.08')
        ),
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2028,
            end_year=2029,
            growth_rate=Decimal('0.06')
        )
    ]
    
    # Test transition to default rate
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2027,  # Gap year
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'default'
    assert result.final_value == Decimal('105000')
    
    # Test transition back to stepwise
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2028,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.rate_source == 'stepwise'
    assert result.final_value == Decimal('106000')

def test_negative_growth_rates():
    """Test handling of negative growth rates."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2026,
            growth_rate=Decimal('-0.05')  # 5% decline
        )
    ]
    
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    assert result.final_value == Decimal('95000')
    assert result.growth_amount == Decimal('-5000')

def test_zero_value_growth():
    """Test growth calculations with zero initial value."""
    handler = GrowthRateHandler()
    result = handler.apply_growth(
        value=Decimal('0'),
        year=2025,
        default_rate=Decimal('0.06'),
        growth_configs=[]
    )
    assert result.final_value == Decimal('0')
    assert result.growth_amount == Decimal('0')

def test_compound_growth_accuracy():
    """Test accuracy of compound growth calculations over multiple periods."""
    handler = GrowthRateHandler()
    initial_value = Decimal('100000')
    rate = Decimal('0.05')
    
    # Calculate 5 years of compound growth
    value = initial_value
    for _ in range(5):
        result = handler.apply_growth(
            value=value,
            year=2025,
            default_rate=rate,
            growth_configs=[]
        )
        value = result.final_value
    
    # Compare with direct compound calculation: 100000 * (1.05)^5
    expected = initial_value * (Decimal('1.05') ** Decimal('5'))
    assert abs(value - expected) < Decimal('0.01')

def test_mixed_growth_periods():
    """Test realistic market cycle scenarios."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2026,
            growth_rate=Decimal('-0.15')  # Market decline
        ),
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2027,
            end_year=2028,
            growth_rate=Decimal('0.20')   # Recovery
        )
    ]
    
    # Test full cycle impact
    value = Decimal('100000')
    for year in range(2025, 2029):
        result = handler.apply_growth(
            value=value,
            year=year,
            default_rate=Decimal('0.06'),
            growth_configs=configs
        )
        value = result.final_value
    
    # Verify recovery math is correct
    # 100k * (1 - 0.15) * (1 + 0.20) = 102k
    expected = Decimal('100000') * Decimal('0.85') * Decimal('1.20')
    assert abs(value - expected) < Decimal('0.01')

def test_growth_rate_precision():
    """Test handling of precise decimal growth rates."""
    handler = GrowthRateHandler()
    configs = [
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2026,
            growth_rate=Decimal('0.0567')  # Precise rate
        )
    ]
    
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    expected = Decimal('100000') * (Decimal('1') + Decimal('0.0567'))
    assert abs(result.final_value - expected) < Decimal('0.01')