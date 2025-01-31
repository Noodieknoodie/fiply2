"""
## Scenarios
- Clone of base facts  
- Inherits all base facts and base assumptions  
- Can override any base fact as well as the fact's parameters (like start and end year)
- Unique: Has retirement spending  
- Retirement spending:  
  - Starts at retirement year  
  - Always inflation adjusted  

## Base Facts
Base facts must remain unchanged while scenarios can modify:
- Asset values and growth
- Liability values and interest
- Cash flow amounts and timing
- Retirement income amounts and timing
- Base assumptions
"""


from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from copy import deepcopy

from ....models import ScenarioOverride
from ....utils.money_utils import to_decimal, apply_annual_inflation

class ScenarioCalculatorHelpers:
    """Helper methods for scenario calculations."""
    
    @staticmethod
    def apply_asset_overrides(
        base_values: Dict[int, Decimal],
        overrides: List[ScenarioOverride]
    ) -> Tuple[Dict[int, Decimal], Dict[int, Decimal]]:
        """
        Applies scenario-specific asset value and growth overrides.
        
        Args:
            base_values: Original asset values
            overrides: List of scenario overrides
            
        Returns:
            Tuple of (new_values, override_impacts)
        """
        new_values = base_values.copy()
        impacts = {}
        
        for override in overrides:
            if override.asset_id:
                original = new_values[override.asset_id]
                new_value = to_decimal(override.override_value)
                impacts[override.asset_id] = new_value - original
                new_values[override.asset_id] = new_value
                
        return new_values, impacts

    @staticmethod
    def apply_liability_overrides(
        base_values: Dict[int, Decimal],
        overrides: List[ScenarioOverride]
    ) -> Tuple[Dict[int, Decimal], Dict[int, Decimal]]:
        """
        Applies scenario-specific liability value and interest overrides.
        
        Args:
            base_values: Original liability values
            overrides: List of scenario overrides
            
        Returns:
            Tuple of (new_values, override_impacts)
        """
        new_values = base_values.copy()
        impacts = {}
        
        for override in overrides:
            if override.liability_id:
                original = new_values[override.liability_id]
                new_value = to_decimal(override.override_value)
                impacts[override.liability_id] = new_value - original
                new_values[override.liability_id] = new_value
                
        return new_values, impacts

    @staticmethod
    def apply_cash_flow_overrides(
        base_flows: Dict[int, Tuple[Decimal, bool]],
        overrides: List[ScenarioOverride]
    ) -> Tuple[Dict[int, Tuple[Decimal, bool]], Dict[int, Decimal]]:
        """
        Applies scenario-specific cash flow amount and timing overrides.
        
        Args:
            base_flows: Original flow amounts and inflation flags
            overrides: List of scenario overrides
            
        Returns:
            Tuple of (new_flows, override_impacts)
        """
        new_flows = base_flows.copy()
        impacts = {}
        
        for override in overrides:
            if override.inflow_outflow_id:
                original_amount, inflation_flag = new_flows[override.inflow_outflow_id]
                if override.override_field == 'annual_amount':
                    new_amount = to_decimal(override.override_value)
                    impacts[override.inflow_outflow_id] = new_amount - original_amount
                    new_flows[override.inflow_outflow_id] = (new_amount, inflation_flag)
                elif override.override_field == 'apply_inflation':
                    new_flows[override.inflow_outflow_id] = (
                        original_amount,
                        override.override_value.lower() == 'true'
                    )
                
        return new_flows, impacts

    @staticmethod
    def is_retirement_spending_active(
        current_year: int,
        retirement_year: int,
        override_retirement_year: Optional[int]
    ) -> bool:
        """
        Determines if retirement spending applies for given year.
        
        Args:
            current_year: Year to check
            retirement_year: Original retirement year
            override_retirement_year: Optional overridden retirement year
            
        Returns:
            True if retirement spending is active
        """
        effective_year = override_retirement_year or retirement_year
        return current_year >= effective_year

    @staticmethod
    def calculate_adjusted_spending(
        base_amount: Decimal,
        inflation_rate: Decimal,
        years_from_retirement: int
    ) -> Decimal:
        """
        Calculates inflation-adjusted retirement spending amount.
        
        Args:
            base_amount: Original spending amount
            inflation_rate: Annual inflation rate
            years_from_retirement: Years since retirement
            
        Returns:
            Inflation-adjusted spending amount
        """
        return apply_annual_inflation(
            base_amount,
            inflation_rate,
            years_from_retirement
        )

    @staticmethod
    def generate_scenario_metadata(
        scenario_id: int,
        base_values: Dict[str, Decimal],
        scenario_values: Dict[str, Decimal],
        override_impacts: Dict[str, Decimal],
        year: int
    ) -> Dict:
        """
        Creates metadata about scenario calculations.
        
        Args:
            scenario_id: ID of scenario
            base_values: Original values
            scenario_values: Values after scenario overrides
            override_impacts: Impact of each override
            year: Calculation year
            
        Returns:
            Dictionary containing calculation metadata
        """
        return {
            'scenario_id': scenario_id,
            'year': year,
            'total_override_impact': sum(override_impacts.values()),
            'override_count': len(override_impacts),
            'net_portfolio_impact': (
                scenario_values['portfolio'] - base_values['portfolio']
            )
        }

    @staticmethod
    def track_override_history(
        current_overrides: Dict[str, Decimal],
        historical_overrides: List[Dict[str, Decimal]],
        year: int
    ) -> Dict[str, List[Tuple[int, Decimal]]]:
        """
        Tracks historical impact of overrides over time.
        
        Args:
            current_overrides: Current override impacts
            historical_overrides: List of previous override impacts
            year: Current year
            
        Returns:
            Dictionary mapping override types to impact history
        """
        history = {}
        
        # Initialize history with current year
        for override_type, impact in current_overrides.items():
            history[override_type] = [(year, impact)]
        
        # Add historical data
        for historical in historical_overrides:
            for override_type, impact in historical.items():
                if override_type in history:
                    history[override_type].append(
                        (historical['year'], impact)
                    )
                    
        return history

    @staticmethod
    def validate_override_consistency(
        overrides: List[ScenarioOverride]
    ) -> None:
        """
        Validates overrides don't conflict with each other.
        
        Args:
            overrides: List of scenario overrides
            
        Raises:
            ValueError if overrides are inconsistent
        """
        # Track overrides by target
        target_overrides = {}
        
        for override in overrides:
            target_id = None
            if override.asset_id:
                target_id = ('asset', override.asset_id)
            elif override.liability_id:
                target_id = ('liability', override.liability_id)
            elif override.inflow_outflow_id:
                target_id = ('flow', override.inflow_outflow_id)
            elif override.retirement_income_plan_id:
                target_id = ('income', override.retirement_income_plan_id)
                
            if target_id:
                if target_id in target_overrides:
                    if override.override_field == target_overrides[target_id]:
                        raise ValueError(
                            f"Conflicting overrides for {target_id[0]} "
                            f"{target_id[1]}: {override.override_field}"
                        )
                target_overrides[target_id] = override.override_field