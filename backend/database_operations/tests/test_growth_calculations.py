# tests/test_growth_calculations.py
from decimal import Decimal
import pytest
from database_operations.calculations.base_facts.growth_handler_calcs import GrowthRateHandler
from database_operations.models import GrowthRateConfiguration

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

def test_override_priority():
    """Test that override takes precedence over stepwise and default."""
    handler = GrowthRateHandler()
    
    configs = [
        GrowthRateConfiguration(
            configuration_type='OVERRIDE',
            start_year=2025,
            growth_rate=Decimal('0.07')
        ),
        GrowthRateConfiguration(
            configuration_type='STEPWISE',
            start_year=2025,
            end_year=2027,
            growth_rate=Decimal('0.08')
        )
    ]
    
    result = handler.apply_growth(
        value=Decimal('100000'),
        year=2025,
        default_rate=Decimal('0.05'),
        growth_configs=configs
    )
    
    assert result.rate_source == 'override'
    assert result.final_value == Decimal('107000')