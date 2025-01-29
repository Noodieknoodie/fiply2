from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from database_operations.models import Base, Household, Plan, Asset, RetirementIncomePlan, GrowthRateConfiguration
from database_operations.connection import get_session
from database_operations.crud.financial.growth_rates import (
    GrowthRateCreate,
    GrowthRateUpdate,
    create_growth_rate,
    get_growth_rate,
    get_asset_growth_rates,
    get_retirement_plan_growth_rates,
    update_growth_rate,
    delete_growth_rate
)
from database_operations.crud.plans import PlanCreate, create_plan
from database_operations.crud.households import HouseholdCreate, create_household
from database_operations.crud.financial.assets import AssetCreate, create_asset
from database_operations.crud.financial.retirement import RetirementIncomePlanCreate, create_retirement_plan

@pytest.fixture(autouse=True)
def cleanup_database(db_session: Session):
    """Cleanup the database before each test."""
    db_session.execute(delete(GrowthRateConfiguration))
    db_session.execute(delete(Asset))
    db_session.execute(delete(RetirementIncomePlan))
    db_session.execute(delete(Plan))
    db_session.execute(delete(Household))
    Base.metadata.create_all(bind=db_session.get_bind())
    yield
    db_session.rollback()

@pytest.fixture
def sample_household(db_session: Session) -> Household:
    """Create a sample household."""
    household = Household(
        household_name="Test Household",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1990, 1, 1)
    )
    db_session.add(household)
    db_session.flush()
    return household

@pytest.fixture
def sample_plan(db_session: Session, sample_household: Household) -> Plan:
    """Create a sample plan."""
    plan = Plan(
        household_id=sample_household.household_id,
        plan_name="Test Plan"
    )
    db_session.add(plan)
    db_session.flush()
    return plan

@pytest.fixture
def sample_asset(db_session: Session, sample_plan: Plan) -> Asset:
    """Create a sample asset."""
    asset = Asset(
        plan_id=sample_plan.plan_id,
        asset_category_id=1,  # We don't need a real category for these tests
        asset_name="Test Asset",
        owner="person1",
        value=100000.0,
        include_in_nest_egg=True
    )
    db_session.add(asset)
    db_session.flush()
    return asset

@pytest.fixture
def sample_retirement_plan(db_session: Session, sample_plan: Plan) -> RetirementIncomePlan:
    """Create a sample retirement income plan."""
    retirement_plan = RetirementIncomePlan(
        plan_id=sample_plan.plan_id,
        name="Test Retirement Plan",
        owner="person1",
        annual_income=50000.0,
        start_age=65,
        include_in_nest_egg=True
    )
    db_session.add(retirement_plan)
    db_session.flush()
    return retirement_plan

def test_create_growth_rate_default(db_session: Session, sample_asset: Asset):
    """Test creating a default growth rate configuration."""
    growth_rate_data = GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="DEFAULT",
        growth_rate=0.07
    )
    growth_rate = create_growth_rate(db_session, growth_rate_data)
    assert growth_rate.asset_id == sample_asset.asset_id
    assert growth_rate.configuration_type == "DEFAULT"
    assert growth_rate.growth_rate == 0.07
    assert growth_rate.start_date is None
    assert growth_rate.end_date is None

def test_create_growth_rate_stepwise(db_session: Session, sample_asset: Asset):
    """Test creating a stepwise growth rate configuration."""
    growth_rate_data = GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="STEPWISE",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        growth_rate=0.05
    )
    growth_rate = create_growth_rate(db_session, growth_rate_data)
    assert growth_rate.configuration_type == "STEPWISE"
    assert growth_rate.start_date == date(2024, 1, 1)
    assert growth_rate.end_date == date(2024, 12, 31)

def test_create_growth_rate_invalid_type(db_session: Session, sample_asset: Asset):
    """Test creating a growth rate with invalid configuration type."""
    growth_rate_data = GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="INVALID",
        growth_rate=0.07
    )
    with pytest.raises(ValueError, match="Invalid configuration_type"):
        create_growth_rate(db_session, growth_rate_data)

def test_create_stepwise_without_dates(db_session: Session, sample_asset: Asset):
    """Test creating a stepwise configuration without dates."""
    growth_rate_data = GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="STEPWISE",
        growth_rate=0.07
    )
    with pytest.raises(ValueError, match="Stepwise configurations require both start_date and end_date"):
        create_growth_rate(db_session, growth_rate_data)

def test_get_growth_rate(db_session: Session, sample_asset: Asset):
    """Test retrieving a growth rate configuration."""
    growth_rate_data = GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="DEFAULT",
        growth_rate=0.07
    )
    created = create_growth_rate(db_session, growth_rate_data)
    retrieved = get_growth_rate(db_session, created.growth_rate_id)
    assert retrieved is not None
    assert retrieved.growth_rate_id == created.growth_rate_id
    assert retrieved.growth_rate == 0.07

def test_get_asset_growth_rates(db_session: Session, sample_asset: Asset):
    """Test retrieving all growth rates for an asset."""
    # Create multiple growth rates
    create_growth_rate(db_session, GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="DEFAULT",
        growth_rate=0.07
    ))
    create_growth_rate(db_session, GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="STEPWISE",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        growth_rate=0.05
    ))
    
    growth_rates = get_asset_growth_rates(db_session, sample_asset.asset_id)
    assert len(growth_rates) == 2
    assert any(gr.configuration_type == "DEFAULT" for gr in growth_rates)
    assert any(gr.configuration_type == "STEPWISE" for gr in growth_rates)

def test_update_growth_rate(db_session: Session, sample_asset: Asset):
    """Test updating a growth rate configuration."""
    growth_rate = create_growth_rate(db_session, GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="DEFAULT",
        growth_rate=0.07
    ))
    
    updated = update_growth_rate(db_session, growth_rate.growth_rate_id, GrowthRateUpdate(
        growth_rate=0.08
    ))
    assert updated is not None
    assert updated.growth_rate == 0.08
    assert updated.configuration_type == "DEFAULT"  # Unchanged

def test_update_nonexistent_growth_rate(db_session: Session):
    """Test updating a non-existent growth rate."""
    result = update_growth_rate(db_session, 999, GrowthRateUpdate(growth_rate=0.08))
    assert result is None

def test_delete_growth_rate(db_session: Session, sample_asset: Asset):
    """Test deleting a growth rate configuration."""
    growth_rate = create_growth_rate(db_session, GrowthRateCreate(
        asset_id=sample_asset.asset_id,
        configuration_type="DEFAULT",
        growth_rate=0.07
    ))
    
    assert delete_growth_rate(db_session, growth_rate.growth_rate_id) is True
    assert get_growth_rate(db_session, growth_rate.growth_rate_id) is None

def test_delete_nonexistent_growth_rate(db_session: Session):
    """Test deleting a non-existent growth rate."""
    assert delete_growth_rate(db_session, 999) is False 