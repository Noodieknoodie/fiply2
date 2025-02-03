# tests/test_crud_operations.py
import pytest
from decimal import Decimal
from database_operations.crud.financial.assets_crud import AssetCRUD
from database_operations.crud.financial.liabilities_crud import LiabilityCRUD
from database_operations.crud.financial.cash_flows_crud import CashFlowCRUD
from database_operations.crud.plans_crud import PlanCRUD

def test_asset_crud_operations(db_session, base_plan_with_facts):
    """Test basic CRUD operations for assets."""
    crud = AssetCRUD(db_session)
    
    # Create
    asset = crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,  # From fixture
        asset_name="Roth IRA",
        value=100000.00,
        owner="person1"
    )
    assert asset.asset_name == "Roth IRA"
    
    # Read
    retrieved = crud.get_asset(asset.asset_id)
    assert retrieved is not None
    assert retrieved.value == 100000.00
    
    # Update
    updated = crud.update_asset(
        asset.asset_id, 
        {"value": 150000.00}
    )
    assert updated.value == 150000.00
    
    # Delete
    assert crud.delete_asset(asset.asset_id)

def test_plan_crud_operations(db_session, base_household):
    """Test CRUD operations for plans."""
    crud = PlanCRUD(db_session)
    
    # Create with current year
    plan = crud.create_plan(
        household_id=base_household.household_id,
        plan_name="New Test Plan"
    )
    assert plan.plan_creation_year is not None
    assert plan.plan_name == "New Test Plan"
    
    # Read
    retrieved = crud.get_plan(plan.plan_id)
    assert retrieved is not None
    
    # Update
    updated = crud.update_plan(
        plan.plan_id,
        {"plan_name": "Updated Plan Name"}
    )
    assert updated.plan_name == "Updated Plan Name"

def test_cash_flow_crud_operations(db_session, base_plan_with_facts):
    """Test CRUD operations for cash flows."""
    crud = CashFlowCRUD(db_session)
    
    # Create
    flow = crud.create_cash_flow(
        plan_id=base_plan_with_facts.plan_id,
        name="Bonus",
        flow_type="inflow",
        annual_amount=50000.00,
        start_year=base_plan_with_facts.plan_creation_year,
        end_year=base_plan_with_facts.plan_creation_year,  # One-time
        apply_inflation=False
    )
    assert flow.annual_amount == 50000.00
    
    # Verify single-year flow
    assert flow.start_year == flow.end_year

def test_crud_validation_handling(db_session, base_plan_with_facts):
    """Test validation handling in CRUD operations."""
    asset_crud = AssetCRUD(db_session)
    
    # Should fail with negative value
    with pytest.raises(ValueError):
        asset_crud.create_asset(
            plan_id=base_plan_with_facts.plan_id,
            asset_category_id=1,
            asset_name="Invalid Asset",
            value=-100000.00,
            owner="person1"
        )
    
    # Should fail with invalid owner
    with pytest.raises(ValueError):
        asset_crud.create_asset(
            plan_id=base_plan_with_facts.plan_id,
            asset_category_id=1,
            asset_name="Invalid Asset",
            value=100000.00,
            owner="invalid_person"  # Must be person1/person2/joint
        )