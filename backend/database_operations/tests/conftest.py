# tests/conftest.py
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from database_operations.models import Base  # Your SQLAlchemy models
from database_operations.models import Household, Plan, BaseAssumption, Asset
from database_operations.utils.money_utils import apply_annual_compound_rate


@pytest.fixture
def db_session():
    """Creates fresh in-memory database for each test"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def basic_household(db_session):
    """Creates a test household"""
    household = Household(
        household_name='Test Family',
        person1_first_name='John',
        person1_last_name='Doe',
        person1_dob=date(1980, 1, 1)
    )
    db_session.add(household)
    db_session.commit()
    return household

@pytest.fixture
def basic_plan(db_session, basic_household):
    """Creates a test plan"""
    plan = Plan(
        household_id=basic_household.id,
        plan_name='Test Plan',
        reference_person=1,
        plan_creation_year=2024
    )
    db_session.add(plan)
    db_session.commit()
    return plan

# tests/test_base_assumptions.py
def test_create_base_assumptions(db_session, basic_plan):
    """Test creating basic assumptions"""
    assumptions = BaseAssumption(
        plan_id=basic_plan.id,
        retirement_age_1=65,
        final_age_1=95,
        default_growth_rate=0.06,
        inflation_rate=0.03
    )
    db_session.add(assumptions)
    db_session.commit()

    loaded = db_session.query(BaseAssumption).first()
    assert loaded.retirement_age_1 == 65
    assert loaded.default_growth_rate == 0.06

def test_prevent_invalid_age_sequence(db_session, basic_plan):
    """Test can't create invalid age sequence"""
    with pytest.raises(ValueError):
        assumptions = BaseAssumption(
            plan_id=basic_plan.id,
            retirement_age_1=95,  # Retirement after final age!
            final_age_1=65,
            default_growth_rate=0.06,
            inflation_rate=0.03
        )
        db_session.add(assumptions)
        db_session.commit()

def test_growth_rate_calculation(db_session, basic_plan):
    """Test growth rate actually compounds correctly"""
    # Set up test data
    assumptions = BaseAssumption(
        plan_id=basic_plan.id,
        retirement_age_1=65,
        final_age_1=95,
        default_growth_rate=0.06,
        inflation_rate=0.03
    )
    db_session.add(assumptions)
    
    asset = Asset(
        plan_id=basic_plan.id,
        asset_category_id=1,
        asset_name='Test Asset',
        owner='person1',
        value=100000.0
    )
    db_session.add(asset)
    db_session.commit()

    # Test calculation
    result = apply_annual_compound_rate(
        Decimal(str(asset.value)), 
        Decimal(str(assumptions.default_growth_rate))
    )
    assert float(round(result, 2)) == 106000.00  # 100k * 1.06