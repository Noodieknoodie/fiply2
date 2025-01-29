"""Tests for inflow and outflow calculations.

This test suite verifies the year-based cash flow calculations,
demonstrating how flows are tracked and calculated on a yearly basis.
"""

import pytest
from decimal import Decimal
from ...calculations.base_facts.inflows_outflows import (
    FlowType,
    CashFlowFact,
    calculate_cash_flow_value,
    aggregate_flows_by_type,
    calculate_total_cash_flows
)

# Test Data
SAMPLE_FLOWS = [
    # Regular income (no end date)
    CashFlowFact(
        annual_amount=100000.00,
        type=FlowType.INFLOW,
        name="Salary",
        start_year=2024,
        end_year=None,
        apply_inflation=True
    ),
    # Inheritance (one-time inflow)
    CashFlowFact(
        annual_amount=500000.00,
        type=FlowType.INFLOW,
        name="Inheritance",
        start_year=2025,
        end_year=2025,
        apply_inflation=False
    ),
    # Regular expense
    CashFlowFact(
        annual_amount=50000.00,
        type=FlowType.OUTFLOW,
        name="Living Expenses",
        start_year=2024,
        end_year=None,
        apply_inflation=True
    )
]


def test_cash_flow_activation():
    """Test when cash flows become active based on years."""
    flow = SAMPLE_FLOWS[1]  # Inheritance in 2025
    
    # Before start year
    result = calculate_cash_flow_value(flow, 2024)
    assert not result['is_active']
    assert result['adjusted_amount'] == 0.0
    
    # During active year
    result = calculate_cash_flow_value(flow, 2025)
    assert result['is_active']
    assert result['adjusted_amount'] == 500000.00
    
    # After end year
    result = calculate_cash_flow_value(flow, 2026)
    assert not result['is_active']
    assert result['adjusted_amount'] == 0.0


def test_inflation_adjustment():
    """Test inflation adjustments over multiple years."""
    flow = SAMPLE_FLOWS[0]  # Salary with inflation
    inflation_rate = 0.03  # 3% inflation
    
    # Start year - no inflation yet
    result = calculate_cash_flow_value(flow, 2024, inflation_rate)
    assert result['adjusted_amount'] == 100000.00
    assert not result['inflation_applied']
    
    # One year of inflation
    result = calculate_cash_flow_value(flow, 2025, inflation_rate)
    assert result['adjusted_amount'] == 103000.00
    assert result['inflation_applied']
    
    # Two years of inflation
    result = calculate_cash_flow_value(flow, 2026, inflation_rate)
    assert abs(result['adjusted_amount'] - 106090.00) < 0.01


def test_flow_aggregation():
    """Test aggregation of multiple flows in a year."""
    year = 2025
    inflation_rate = 0.03
    
    aggregated = aggregate_flows_by_type(SAMPLE_FLOWS, year, inflation_rate)
    
    # Should have both types
    assert FlowType.INFLOW.value in aggregated
    assert FlowType.OUTFLOW.value in aggregated
    
    # Should have correct number of flows
    assert len(aggregated[FlowType.INFLOW.value]) == 2  # Salary + Inheritance
    assert len(aggregated[FlowType.OUTFLOW.value]) == 1  # Living Expenses


def test_total_calculations():
    """Test calculation of total inflows/outflows and net cash flow."""
    year = 2025
    inflation_rate = 0.03
    
    totals = calculate_total_cash_flows(SAMPLE_FLOWS, year, inflation_rate)
    
    # Expected values for 2025:
    # Inflows: Salary (103,000) + Inheritance (500,000) = 603,000
    # Outflows: Living Expenses (51,500)
    # Net: 551,500
    assert abs(totals['total_inflows'] - 603000.00) < 0.01
    assert abs(totals['total_outflows'] - 51500.00) < 0.01
    assert abs(totals['net_cash_flow'] - 551500.00) < 0.01


def test_metadata_tracking():
    """Test tracking of active vs total flows."""
    year = 2025
    totals = calculate_total_cash_flows(SAMPLE_FLOWS, year)
    
    assert totals['metadata']['inflows']['total'] == 2
    assert totals['metadata']['inflows']['active'] == 2
    assert totals['metadata']['outflows']['total'] == 1
    assert totals['metadata']['outflows']['active'] == 1


def test_base_year_override():
    """Test using a different base year for inflation calculations."""
    flow = SAMPLE_FLOWS[0]  # Salary with inflation
    inflation_rate = 0.03
    
    # Calculate with default base year (start_year)
    result1 = calculate_cash_flow_value(flow, 2026, inflation_rate)
    
    # Calculate with explicit base year
    result2 = calculate_cash_flow_value(flow, 2026, inflation_rate, base_year=2023)
    
    # Should have more inflation applied with earlier base year
    assert result2['adjusted_amount'] > result1['adjusted_amount']


def test_decimal_precision():
    """Test handling of decimal precision in calculations."""
    # Create a flow with an odd amount to test rounding
    flow = CashFlowFact(
        annual_amount=100000.33,
        type=FlowType.INFLOW,
        name="Test",
        start_year=2024,
        end_year=None,
        apply_inflation=True
    )
    
    result = calculate_cash_flow_value(flow, 2024)
    
    # Should maintain 2 decimal places
    assert isinstance(result['annual_amount'], float)
    assert str(result['annual_amount']).split('.')[1] == '33' 