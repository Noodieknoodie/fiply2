from datetime import date
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete

from ..models import Plan, Household, AssetCategory, Asset, Base
from ..connection import get_session
from ..crud.financial.assets import (
    AssetCategoryCreate,
    AssetCategoryUpdate,
    AssetCreate,
    AssetUpdate,
    create_asset_category,
    get_asset_category,
    get_plan_asset_categories,
    update_asset_category,
    delete_asset_category,
    reorder_asset_categories,
    create_asset,
    get_asset,
    get_category_assets,
    get_plan_assets,
    update_asset,
    delete_asset
)
from ..crud.plans import PlanCreate, create_plan
from ..crud.households import HouseholdCreate, create_household

@pytest.fixture(autouse=True)
def cleanup_database():
    """Cleanup the database before each test."""
    session = get_session()
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=session.get_bind())
        # Recreate all tables with current schema
        Base.metadata.create_all(bind=session.get_bind())
        session.commit()
    finally:
        session.close()

@pytest.fixture
def db_session():
    """Fixture that provides a database session."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_household(db_session: Session):
    """Create a sample household for testing."""
    household_data = HouseholdCreate(
        household_name="Test Family",
        person1_first_name="John",
        person1_last_name="Doe",
        person1_dob=date(1980, 1, 1)
    )
    return create_household(db_session, household_data)

@pytest.fixture
def sample_plan(db_session: Session, sample_household: Household):
    """Create a sample plan for testing."""
    plan_data = PlanCreate(
        household_id=sample_household.household_id,
        plan_name="Test Plan"
    )
    return create_plan(db_session, plan_data)

@pytest.fixture
def sample_category_data(sample_plan: Plan):
    """Create sample category data."""
    return AssetCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Test Category"
    )

@pytest.fixture
def sample_category(db_session: Session, sample_category_data: AssetCategoryCreate):
    """Create a sample asset category for testing."""
    return create_asset_category(db_session, sample_category_data)

@pytest.fixture
def sample_asset_data(sample_plan: Plan, sample_category: AssetCategory):
    """Create sample asset data."""
    return AssetCreate(
        plan_id=sample_plan.plan_id,
        asset_category_id=sample_category.asset_category_id,
        asset_name="Test Asset",
        owner="Person 1",
        value=100000.0
    )

def test_create_asset_category(db_session: Session, sample_category_data: AssetCategoryCreate):
    """Test creating an asset category."""
    category = create_asset_category(db_session, sample_category_data)
    
    assert category.plan_id == sample_category_data.plan_id
    assert category.category_name == "Test Category"
    assert category.category_order == 1  # First category should be order 1

def test_get_asset_category(db_session: Session, sample_category: AssetCategory):
    """Test retrieving an asset category by ID."""
    retrieved_category = get_asset_category(db_session, sample_category.asset_category_id)
    
    assert retrieved_category is not None
    assert retrieved_category.asset_category_id == sample_category.asset_category_id
    assert retrieved_category.category_name == sample_category.category_name

def test_get_nonexistent_category(db_session: Session):
    """Test retrieving a non-existent category."""
    category = get_asset_category(db_session, 999)
    assert category is None

def test_get_plan_asset_categories(db_session: Session, sample_plan: Plan):
    """Test retrieving all categories for a plan."""
    # Create multiple categories
    category_data1 = AssetCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 1"
    )
    category_data2 = AssetCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 2"
    )
    
    create_asset_category(db_session, category_data1)
    create_asset_category(db_session, category_data2)
    
    categories = get_plan_asset_categories(db_session, sample_plan.plan_id)
    assert len(categories) == 2
    assert all(c.plan_id == sample_plan.plan_id for c in categories)
    assert categories[0].category_order < categories[1].category_order

def test_update_asset_category(db_session: Session, sample_category: AssetCategory):
    """Test updating an asset category."""
    update_data = AssetCategoryUpdate(
        category_name="Updated Category",
        category_order=5
    )
    
    updated_category = update_asset_category(db_session, sample_category.asset_category_id, update_data)
    assert updated_category is not None
    assert updated_category.category_name == "Updated Category"
    assert updated_category.category_order == 5

def test_delete_asset_category(db_session: Session, sample_category: AssetCategory):
    """Test deleting an asset category."""
    assert delete_asset_category(db_session, sample_category.asset_category_id) is True
    assert get_asset_category(db_session, sample_category.asset_category_id) is None

def test_reorder_asset_categories(db_session: Session, sample_plan: Plan):
    """Test reordering asset categories."""
    # Create multiple categories
    cat1 = create_asset_category(db_session, AssetCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 1"
    ))
    cat2 = create_asset_category(db_session, AssetCategoryCreate(
        plan_id=sample_plan.plan_id,
        category_name="Category 2"
    ))
    
    # Swap their orders
    new_orders = {
        cat1.asset_category_id: 2,
        cat2.asset_category_id: 1
    }
    
    updated_categories = reorder_asset_categories(db_session, sample_plan.plan_id, new_orders)
    assert len(updated_categories) == 2
    assert updated_categories[0].asset_category_id == cat2.asset_category_id
    assert updated_categories[1].asset_category_id == cat1.asset_category_id

def test_create_asset(db_session: Session, sample_asset_data: AssetCreate):
    """Test creating an asset."""
    asset = create_asset(db_session, sample_asset_data)
    
    assert asset.plan_id == sample_asset_data.plan_id
    assert asset.asset_category_id == sample_asset_data.asset_category_id
    assert asset.asset_name == "Test Asset"
    assert asset.owner == "Person 1"
    assert asset.value == 100000.0
    assert asset.include_in_nest_egg == True

def test_get_asset(db_session: Session, sample_asset_data: AssetCreate):
    """Test retrieving an asset by ID."""
    created_asset = create_asset(db_session, sample_asset_data)
    retrieved_asset = get_asset(db_session, created_asset.asset_id)
    
    assert retrieved_asset is not None
    assert retrieved_asset.asset_id == created_asset.asset_id
    assert retrieved_asset.asset_name == created_asset.asset_name

def test_get_category_assets(db_session: Session, sample_category: AssetCategory, sample_asset_data: AssetCreate):
    """Test retrieving all assets in a category."""
    # Create multiple assets
    asset_data1 = AssetCreate(
        plan_id=sample_asset_data.plan_id,
        asset_category_id=sample_category.asset_category_id,
        asset_name="Asset 1",
        owner="Person 1",
        value=50000.0
    )
    asset_data2 = AssetCreate(
        plan_id=sample_asset_data.plan_id,
        asset_category_id=sample_category.asset_category_id,
        asset_name="Asset 2",
        owner="Person 2",
        value=75000.0
    )
    
    create_asset(db_session, asset_data1)
    create_asset(db_session, asset_data2)
    
    assets = get_category_assets(db_session, sample_category.asset_category_id)
    assert len(assets) == 2
    assert all(a.asset_category_id == sample_category.asset_category_id for a in assets)

def test_get_plan_assets(
    db_session: Session, 
    sample_plan: Plan, 
    sample_category: AssetCategory, 
    sample_asset_data: AssetCreate
):
    """Test retrieving all assets for a plan."""
    # Create multiple assets
    asset_data1 = AssetCreate(
        plan_id=sample_plan.plan_id,
        asset_category_id=sample_category.asset_category_id,
        asset_name="Asset 1",
        owner="Person 1",
        value=50000.0
    )
    asset_data2 = AssetCreate(
        plan_id=sample_plan.plan_id,
        asset_category_id=sample_category.asset_category_id,
        asset_name="Asset 2",
        owner="Person 2",
        value=75000.0
    )
    
    create_asset(db_session, asset_data1)
    create_asset(db_session, asset_data2)
    
    # Test without categories
    assets = get_plan_assets(db_session, sample_plan.plan_id)
    assert len(assets) == 2
    assert all(a.plan_id == sample_plan.plan_id for a in assets)
    
    # Test with categories
    assets = get_plan_assets(db_session, sample_plan.plan_id, include_categories=True)
    assert len(assets) == 2
    assert all(a.category.asset_category_id == sample_category.asset_category_id for a in assets)

def test_update_asset(db_session: Session, sample_asset_data: AssetCreate):
    """Test updating an asset."""
    asset = create_asset(db_session, sample_asset_data)
    
    update_data = AssetUpdate(
        asset_name="Updated Asset",
        value=150000.0,
        include_in_nest_egg=False
    )
    
    updated_asset = update_asset(db_session, asset.asset_id, update_data)
    assert updated_asset is not None
    assert updated_asset.asset_name == "Updated Asset"
    assert updated_asset.value == 150000.0
    assert updated_asset.include_in_nest_egg == False
    assert updated_asset.owner == "Person 1"

def test_delete_asset(db_session: Session, sample_asset_data: AssetCreate):
    """Test deleting an asset."""
    asset = create_asset(db_session, sample_asset_data)
    
    assert delete_asset(db_session, asset.asset_id) is True
    assert get_asset(db_session, asset.asset_id) is None 