"""Tests for base facts inflow and outflow calculations."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from ...models import InflowOutflow, Plan
from ...calculations.base_facts.inflows_outflows import (
    CashFlowFact,
    calculate_cash_flow_value,
    aggregate_flows_by_type,
    calculate_total_cash_flows,
    FlowType
)

# Test Data
BASE_DATE = date(2025, 1, 1)
ONE_YEAR_LATER = BASE_DATE + timedelta(days=365)
SIX_MONTHS_LATER = BASE_DATE + timedelta(days=182)

SAMPLE_FLOWS = [
    {
        'annual_amount': 120000.0,
        'type': 'inflow',
        'name': 'Salary',
        'start_date': BASE_DATE,
        'end_date': None,
        'apply_inflation': True
    },
    {
        'annual_amount': 24000.0,
        'type': 'outflow',
        'name': 'Rent',
        'start_date': BASE_DATE,
        'end_date': ONE_YEAR_LATER,
        'apply_inflation': False
    },
    {
        'annual_amount': 6000.0,
        'type': 'outflow',
        'name': 'Car Payment',
        'start_date': SIX_MONTHS_LATER,
        'end_date': None,
        'apply_inflation': False
    }
]

@pytest.fixture
def sample_flow():
    """Create a sample cash flow for testing."""
    return CashFlowFact.from_db_row(SAMPLE_FLOWS[0])  # Using Salary as default test flow

@pytest.fixture
def real_flows(db_session):
    """Load real flows from Test Household A (plan_id=1)."""
    stmt = select(InflowOutflow).join(Plan).filter(Plan.plan_id == 1)
    flows = db_session.execute(stmt).scalars().all()
    return [CashFlowFact.from_db_row({
        'annual_amount': flow.annual_amount,
        'type': flow.type,
        'name': flow.name,
        'start_date': flow.start_date,
        'end_date': flow.end_date,
        'apply_inflation': flow.apply_inflation
    }) for flow in flows]

def test_cash_flow_fact_creation():
    """Test creation of CashFlowFact from database row."""
    flow = CashFlowFact.from_db_row(SAMPLE_FLOWS[0])
    assert flow.annual_amount == 120000.0
    assert flow.type == FlowType.INFLOW
    assert flow.name == 'Salary'
    assert flow.start_date == BASE_DATE
    assert flow.end_date is None
    assert flow.apply_inflation == True

def test_calculate_cash_flow_value_inactive():
    """Test cash flow calculation for inactive flow."""
    flow = CashFlowFact.from_db_row(SAMPLE_FLOWS[2])  # Car payment starts in 6 months
    result = calculate_cash_flow_value(flow, BASE_DATE)
    
    assert result['annual_amount'] == 6000.0
    assert result['adjusted_amount'] == 0.0
    assert result['is_active'] == False
    assert result['inflation_applied'] == False

def test_calculate_cash_flow_value_with_inflation():
    """Test cash flow calculation with inflation adjustment."""
    flow = CashFlowFact.from_db_row(SAMPLE_FLOWS[0])  # Salary with inflation
    result = calculate_cash_flow_value(
        flow,
        ONE_YEAR_LATER,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    expected = float(
        (Decimal('120000') * (Decimal('1') + Decimal('0.03')) ** Decimal('1'))
        .quantize(Decimal('0.01'))
    )
    
    assert result['annual_amount'] == 120000.0
    assert abs(result['adjusted_amount'] - expected) < 0.01
    assert result['is_active'] == True
    assert result['inflation_applied'] == True

def test_calculate_cash_flow_value_no_inflation():
    """Test cash flow calculation without inflation adjustment."""
    flow = CashFlowFact.from_db_row(SAMPLE_FLOWS[1])  # Rent without inflation
    result = calculate_cash_flow_value(
        flow,
        SIX_MONTHS_LATER,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    assert result['annual_amount'] == 24000.0
    assert result['adjusted_amount'] == 24000.0
    assert result['is_active'] == True
    assert result['inflation_applied'] == False

def test_calculate_cash_flow_value_with_end_date():
    """Test cash flow calculation with end date consideration."""
    flow = CashFlowFact.from_db_row(SAMPLE_FLOWS[1])  # Rent ends after 1 year
    
    # Test before end date
    result = calculate_cash_flow_value(flow, SIX_MONTHS_LATER, base_date=BASE_DATE)
    assert result['is_active'] == True
    assert result['adjusted_amount'] == 24000.0
    
    # Test after end date
    result = calculate_cash_flow_value(
        flow,
        ONE_YEAR_LATER + timedelta(days=1),
        base_date=BASE_DATE
    )
    assert result['is_active'] == False
    assert result['adjusted_amount'] == 0.0

def test_aggregate_flows_by_type():
    """Test grouping and calculating flows by type."""
    flows = [CashFlowFact.from_db_row(row) for row in SAMPLE_FLOWS]
    results = aggregate_flows_by_type(flows, SIX_MONTHS_LATER, base_date=BASE_DATE)
    
    assert len(results['inflow']) == 1
    assert len(results['outflow']) == 2
    
    # Check inflow (Salary)
    assert results['inflow'][0]['annual_amount'] == 120000.0
    assert results['inflow'][0]['is_active'] == True
    
    # Check outflows (Rent active, Car Payment not yet active)
    active_outflows = [f for f in results['outflow'] if f['is_active']]
    assert len(active_outflows) == 1
    assert active_outflows[0]['annual_amount'] == 24000.0

def test_calculate_total_cash_flows():
    """Test calculation of total cash flow values."""
    flows = [CashFlowFact.from_db_row(row) for row in SAMPLE_FLOWS]
    result = calculate_total_cash_flows(flows, SIX_MONTHS_LATER, base_date=BASE_DATE)
    
    # At 6 months: Salary (120000) active, Rent (24000) active, Car Payment not yet active
    assert abs(result['total_inflows'] - 120000.0) < 0.01
    assert abs(result['total_outflows'] - 24000.0) < 0.01
    assert abs(result['net_cash_flow'] - 96000.0) < 0.01
    
    assert result['metadata']['inflows']['total'] == 1
    assert result['metadata']['inflows']['active'] == 1
    assert result['metadata']['outflows']['total'] == 2
    assert result['metadata']['outflows']['active'] == 1

def test_calculate_total_cash_flows_with_inflation():
    """Test calculation of total cash flows with inflation adjustment."""
    flows = [CashFlowFact.from_db_row(row) for row in SAMPLE_FLOWS]
    result = calculate_total_cash_flows(
        flows,
        ONE_YEAR_LATER,
        inflation_rate=0.03,
        base_date=BASE_DATE
    )
    
    # Calculate expected salary with inflation
    expected_salary = float(
        (Decimal('120000') * (Decimal('1') + Decimal('0.03')))
        .quantize(Decimal('0.01'))
    )
    
    # At 1 year: Salary with inflation, Rent still active, Car Payment active
    assert abs(result['total_inflows'] - expected_salary) < 0.01
    assert abs(result['total_outflows'] - 30000.0) < 0.01  # 24000 + 6000
    assert abs(result['net_cash_flow'] - (expected_salary - 30000.0)) < 0.01

def test_real_data_calculations(real_flows):
    """Test calculations with real data from the database."""
    result = calculate_total_cash_flows(real_flows, BASE_DATE)
    
    # Calculate expected totals directly
    active_flows = [
        f for f in real_flows
        if f.start_date <= BASE_DATE and (f.end_date is None or BASE_DATE <= f.end_date)
    ]
    
    expected_inflows = sum(
        f.annual_amount for f in active_flows
        if f.type == FlowType.INFLOW
    )
    expected_outflows = sum(
        f.annual_amount for f in active_flows
        if f.type == FlowType.OUTFLOW
    )
    
    assert abs(result['total_inflows'] - expected_inflows) < 0.01
    assert abs(result['total_outflows'] - expected_outflows) < 0.01
    assert abs(result['net_cash_flow'] - (expected_inflows - expected_outflows)) < 0.01

def test_real_data_with_inflation(real_flows):
    """Test real data calculations with inflation adjustment."""
    inflation_rate = 0.03
    future_date = BASE_DATE + timedelta(days=365 * 2)  # 2 years in future
    
    result = calculate_total_cash_flows(
        real_flows,
        future_date,
        inflation_rate=inflation_rate,
        base_date=BASE_DATE
    )
    
    # Verify inflation is only applied to flows with apply_inflation=True
    aggregated = aggregate_flows_by_type(
        real_flows,
        future_date,
        inflation_rate=inflation_rate,
        base_date=BASE_DATE
    )
    
    for flow_type in ['inflow', 'outflow']:
        for flow in aggregated[flow_type]:
            if flow['inflation_applied']:
                assert flow['adjusted_amount'] > flow['annual_amount']
            elif flow['is_active']:
                assert flow['adjusted_amount'] == flow['annual_amount'] 