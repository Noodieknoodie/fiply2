# tests/test_growth_configurations.py
from decimal import Decimal
import pytest
from database_operations.crud.financial.growth_rates_crud import GrowthRateCRUD
from database_operations.validation.growth_validation import validate_stepwise_periods

def test_validate_stepwise_periods():
    """Test validation of stepwise growth period configurations."""
    # Valid configurations
    valid_periods = [
        {"start_year": 2025, "end_year": 2027},
        {"start_year": 2028, "end_year": 2030}
    ]
    assert validate_stepwise_periods(valid_periods, "test") is None
    
    # Overlapping periods
    invalid_periods = [
        {"start_year": 2025, "end_year": 2028},
        {"start_year": 2027, "end_year": 2030}
    ]
    with pytest.raises(ValueError, match="test contains overlapping periods"):
        validate_stepwise_periods(invalid_periods, "test")

def test_growth_rate_crud(db_session, base_plan_with_facts):
    """Test CRUD operations for growth rate configurations."""
    crud = GrowthRateCRUD(db_session)
    
    # Test creating override growth rate
    config = crud.create_growth_config(
        configuration_type="OVERRIDE",
        start_year=2025,
        growth_rate=0.08,
        asset_id=1  # From base_plan_with_facts fixture
    )
    
    assert config.growth_rate == 0.08
    assert config.configuration_type == "OVERRIDE"

def test_stepwise_growth_configuration(db_session, base_plan_with_facts):
    """Test creation and validation of stepwise growth configurations."""
    crud = GrowthRateCRUD(db_session)
    
    # Create valid stepwise configuration
    configs = crud.create_stepwise_config([
        {
            "start_year": 2025,
            "end_year": 2027,
            "growth_rate": 0.08
        },
        {
            "start_year": 2028,
            "end_year": 2030,
            "growth_rate": 0.06
        }
    ], asset_id=1)
    
    assert len(configs) == 2
    assert configs[0].configuration_type == "STEPWISE"
    assert configs[0].growth_rate == 0.08