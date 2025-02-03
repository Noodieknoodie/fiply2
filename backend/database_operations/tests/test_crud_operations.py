# tests/test_crud_operations.py
import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from database_operations.crud.financial.assets_crud import AssetCRUD
from database_operations.crud.financial.liabilities_crud import LiabilityCRUD
from database_operations.crud.financial.cash_flows_crud import CashFlowCRUD
from database_operations.crud.plans_crud import PlanCRUD
from database_operations.models import Asset, Liability, Plan, CashFlow

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

def test_transaction_isolation(db_session, base_plan_with_facts):
    """Test transaction isolation levels and concurrent modifications."""
    crud = AssetCRUD(db_session)
    
    # Create initial asset
    asset = crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,
        asset_name="Test Asset",
        value=100000.00,
        owner="person1"
    )
    
    # Start a new transaction
    with db_session.begin_nested():
        # Modify asset within transaction
        crud.update_asset(
            asset.asset_id,
            {"value": 150000.00}
        )
        
        # Verify value is updated within transaction
        modified = crud.get_asset(asset.asset_id)
        assert modified.value == 150000.00
        
        # Rollback transaction
        db_session.rollback()
    
    # Verify original value is restored
    original = crud.get_asset(asset.asset_id)
    assert original.value == 100000.00

def test_complex_transaction_rollback(db_session, base_plan_with_facts):
    """Test rollback of complex operations involving multiple entities."""
    asset_crud = AssetCRUD(db_session)
    liability_crud = LiabilityCRUD(db_session)
    
    try:
        # Start transaction
        with db_session.begin_nested():
            # Create asset
            asset = asset_crud.create_asset(
                plan_id=base_plan_with_facts.plan_id,
                asset_category_id=1,
                asset_name="House",
                value=500000.00,
                owner="joint"
            )
            
            # Create related liability (mortgage)
            liability = liability_crud.create_liability(
                plan_id=base_plan_with_facts.plan_id,
                liability_category_id=1,
                liability_name="Mortgage",
                value=400000.00,
                owner="joint",
                interest_rate=0.035
            )
            
            # Simulate error condition
            raise ValueError("Simulated error")
            
    except ValueError:
        db_session.rollback()
    
    # Verify nothing was committed
    assert asset_crud.get_asset(asset.asset_id) is None
    assert liability_crud.get_liability(liability.liability_id) is None

def test_concurrent_modifications(db_session, base_plan_with_facts):
    """Test handling of concurrent modifications to the same entity."""
    crud = AssetCRUD(db_session)
    
    # Create test asset
    asset = crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,
        asset_name="Test Asset",
        value=100000.00,
        owner="person1"
    )
    
    # Simulate concurrent sessions
    session1 = db_session
    session2 = db_session.session_factory()
    
    try:
        # Modify in session 1
        crud1 = AssetCRUD(session1)
        crud1.update_asset(asset.asset_id, {"value": 150000.00})
        
        # Modify in session 2
        crud2 = AssetCRUD(session2)
        with pytest.raises(Exception):  # Expect concurrent modification error
            crud2.update_asset(asset.asset_id, {"value": 200000.00})
            
    finally:
        session2.close()

def test_database_constraints(db_session, base_plan_with_facts):
    """Test enforcement of database constraints."""
    crud = AssetCRUD(db_session)
    
    # Test foreign key constraint
    with pytest.raises(IntegrityError):
        crud.create_asset(
            plan_id=999999,  # Non-existent plan
            asset_category_id=1,
            asset_name="Invalid Asset",
            value=100000.00,
            owner="person1"
        )
    
    # Test unique constraint
    asset1 = crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,
        asset_name="Unique Asset",
        value=100000.00,
        owner="person1"
    )
    
    with pytest.raises(IntegrityError):
        # Attempt to create asset with same name in same plan
        crud.create_asset(
            plan_id=base_plan_with_facts.plan_id,
            asset_category_id=1,
            asset_name="Unique Asset",  # Duplicate name
            value=200000.00,
            owner="person1"
        )

def test_cascade_operations(db_session, base_plan_with_facts):
    """Test cascade behavior for related entities."""
    plan_crud = PlanCRUD(db_session)
    asset_crud = AssetCRUD(db_session)
    
    # Create plan with assets
    plan = plan_crud.create_plan(
        household_id=base_plan_with_facts.household_id,
        plan_name="Cascade Test Plan"
    )
    
    asset = asset_crud.create_asset(
        plan_id=plan.plan_id,
        asset_category_id=1,
        asset_name="Test Asset",
        value=100000.00,
        owner="person1"
    )
    
    # Delete plan and verify cascade
    plan_crud.delete_plan(plan.plan_id)
    
    # Verify asset was cascade deleted
    assert asset_crud.get_asset(asset.asset_id) is None

def test_transaction_deadlock_handling(db_session, base_plan_with_facts):
    """Test handling of potential deadlock scenarios."""
    asset_crud = AssetCRUD(db_session)
    liability_crud = LiabilityCRUD(db_session)
    
    # Create test entities
    asset = asset_crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,
        asset_name="Deadlock Test Asset",
        value=100000.00,
        owner="person1"
    )
    
    liability = liability_crud.create_liability(
        plan_id=base_plan_with_facts.plan_id,
        liability_category_id=1,
        liability_name="Deadlock Test Liability",
        value=50000.00,
        owner="person1",
        interest_rate=0.035
    )
    
    # Simulate deadlock scenario
    session1 = db_session
    session2 = db_session.session_factory()
    
    try:
        with session1.begin_nested():
            # Update asset in session 1
            asset_crud1 = AssetCRUD(session1)
            asset_crud1.update_asset(asset.asset_id, {"value": 150000.00})
            
            with session2.begin_nested():
                # Try to update liability in session 2
                liability_crud2 = LiabilityCRUD(session2)
                liability_crud2.update_liability(
                    liability.liability_id,
                    {"value": 60000.00}
                )
                
                # This should raise a deadlock error
                with pytest.raises(Exception):
                    asset_crud2 = AssetCRUD(session2)
                    asset_crud2.update_asset(asset.asset_id, {"value": 200000.00})
    
    finally:
        session2.close()

def test_bulk_operations(db_session, base_plan_with_facts):
    """Test handling of bulk create/update operations."""
    crud = AssetCRUD(db_session)
    
    # Bulk create assets
    assets_data = [
        {
            "plan_id": base_plan_with_facts.plan_id,
            "asset_category_id": 1,
            "asset_name": f"Bulk Asset {i}",
            "value": 100000.00 * i,
            "owner": "person1"
        }
        for i in range(1, 6)
    ]
    
    created_assets = crud.bulk_create_assets(assets_data)
    assert len(created_assets) == 5
    
    # Bulk update assets
    updates = [
        {"asset_id": asset.asset_id, "value": asset.value * 1.1}
        for asset in created_assets
    ]
    
    updated_assets = crud.bulk_update_assets(updates)
    assert len(updated_assets) == 5
    assert all(
        updated.value > original.value 
        for updated, original in zip(updated_assets, created_assets)
    )

def test_audit_trail(db_session, base_plan_with_facts):
    """Test audit trail for CRUD operations."""
    crud = AssetCRUD(db_session)
    
    # Create asset with audit
    asset = crud.create_asset(
        plan_id=base_plan_with_facts.plan_id,
        asset_category_id=1,
        asset_name="Audit Test Asset",
        value=100000.00,
        owner="person1"
    )
    assert asset.created_at is not None
    
    # Update asset
    updated = crud.update_asset(
        asset.asset_id,
        {"value": 150000.00}
    )
    assert updated.updated_at is not None
    assert updated.updated_at > updated.created_at
