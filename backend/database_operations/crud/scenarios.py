# backend/database_operations/crud/scenarios.py

"""
Full CRUD operations for scenarios following SQLAlchemy 2.0 style
Support for scenario assumptions with proper validation
Granular override management for financial components
Optional eager loading of relationships
Comprehensive scenario summary including override counts
Proper error handling and transaction management
Follows core validation rules from documentation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import (
    Scenario, 
    ScenarioAssumption, 
    ScenarioOverride,
    Plan
)
from ..utils.money_validations import validate_positive_amount, validate_rate

class ScenarioCRUD:
    """CRUD operations for scenario management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_scenario(
        self,
        plan_id: int,
        scenario_name: str,
        scenario_color: Optional[str] = None,
        assumptions: Optional[Dict[str, Any]] = None,
    ) -> Scenario:
        """
        Create a new scenario for a plan.
        
        Args:
            plan_id: ID of plan this scenario belongs to
            scenario_name: Name identifier for the scenario
            scenario_color: Optional color for UI visualization
            assumptions: Optional dict of initial assumption overrides
            
        Returns:
            Newly created Scenario instance
            
        Raises:
            NoResultFound: If plan_id doesn't exist
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Verify plan exists
        stmt = select(Plan).where(Plan.plan_id == plan_id)
        if not self.session.execute(stmt).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} not found")

        # Create scenario instance
        scenario = Scenario(
            plan_id=plan_id,
            scenario_name=scenario_name,
            scenario_color=scenario_color
        )
        
        try:
            self.session.add(scenario)
            self.session.flush()  # Get scenario_id without committing

            # Create assumptions if provided
            if assumptions:
                # Validate rates if provided
                if 'default_growth_rate' in assumptions:
                    validate_rate(assumptions['default_growth_rate'], "default_growth_rate")
                if 'inflation_rate' in assumptions:
                    validate_rate(assumptions['inflation_rate'], "inflation_rate")
                
                # Validate retirement spending if provided
                if 'annual_retirement_spending' in assumptions:
                    validate_positive_amount(
                        assumptions['annual_retirement_spending'], 
                        "annual_retirement_spending"
                    )

                scenario_assumptions = ScenarioAssumption(
                    scenario_id=scenario.scenario_id,
                    **assumptions
                )
                self.session.add(scenario_assumptions)

            self.session.commit()
            return scenario

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create scenario", orig=e)

    def get_scenario(
        self, 
        scenario_id: int, 
        include_assumptions: bool = False,
        include_overrides: bool = False
    ) -> Optional[Scenario]:
        """
        Retrieve a scenario by ID.
        
        Args:
            scenario_id: Primary key of scenario
            include_assumptions: If True, eagerly loads assumption overrides
            include_overrides: If True, eagerly loads component overrides
            
        Returns:
            Scenario instance if found, None otherwise
        """
        stmt = select(Scenario).where(Scenario.scenario_id == scenario_id)
        
        if include_assumptions:
            stmt = stmt.options(joinedload(Scenario.assumptions))
        if include_overrides:
            stmt = stmt.options(joinedload(Scenario.overrides))
            
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_scenarios(self, plan_id: int) -> List[Scenario]:
        """
        Retrieve all scenarios for a specific plan.
        
        Args:
            plan_id: ID of plan to get scenarios for
            
        Returns:
            List of Scenario instances
        """
        stmt = select(Scenario).where(Scenario.plan_id == plan_id)
        return list(self.session.execute(stmt).scalars().all())

    def update_scenario(
        self,
        scenario_id: int,
        update_data: Dict[str, Any],
        assumption_updates: Optional[Dict[str, Any]] = None
    ) -> Optional[Scenario]:
        """
        Update a scenario and optionally its assumptions.
        
        Args:
            scenario_id: Primary key of scenario to update
            update_data: Dictionary of scenario fields to update
            assumption_updates: Optional dictionary of assumption fields to update
            
        Returns:
            Updated Scenario instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        try:
            # Update scenario
            stmt = (
                update(Scenario)
                .where(Scenario.scenario_id == scenario_id)
                .values(**update_data)
                .returning(Scenario)
            )
            result = self.session.execute(stmt)
            scenario = result.scalar_one_or_none()
            
            if not scenario:
                return None

            # Update assumptions if provided
            if assumption_updates:
                # Validate rates if provided
                if 'default_growth_rate' in assumption_updates:
                    validate_rate(assumption_updates['default_growth_rate'], "default_growth_rate")
                if 'inflation_rate' in assumption_updates:
                    validate_rate(assumption_updates['inflation_rate'], "inflation_rate")
                
                # Validate retirement spending if provided
                if 'annual_retirement_spending' in assumption_updates:
                    validate_positive_amount(
                        assumption_updates['annual_retirement_spending'], 
                        "annual_retirement_spending"
                    )

                stmt = (
                    update(ScenarioAssumption)
                    .where(ScenarioAssumption.scenario_id == scenario_id)
                    .values(**assumption_updates)
                )
                self.session.execute(stmt)

            self.session.commit()
            return scenario

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update scenario", orig=e)

    def add_override(
        self,
        scenario_id: int,
        override_field: str,
        override_value: str,
        asset_id: Optional[int] = None,
        liability_id: Optional[int] = None,
        inflow_outflow_id: Optional[int] = None,
        retirement_income_plan_id: Optional[int] = None
    ) -> ScenarioOverride:
        """
        Add a new override to a scenario.
        
        Args:
            scenario_id: ID of scenario to add override to
            override_field: Name of field being overridden
            override_value: New value for the field
            asset_id: Optional ID of asset being overridden
            liability_id: Optional ID of liability being overridden
            inflow_outflow_id: Optional ID of cash flow being overridden
            retirement_income_plan_id: Optional ID of retirement income being overridden
            
        Returns:
            Newly created ScenarioOverride instance
            
        Raises:
            ValueError: If no valid target provided for override
            IntegrityError: If database constraint violated
        """
        # Verify at least one override target is provided
        if not any([asset_id, liability_id, inflow_outflow_id, retirement_income_plan_id]):
            raise ValueError("Must provide a target for the override")

        override = ScenarioOverride(
            scenario_id=scenario_id,
            override_field=override_field,
            override_value=override_value,
            asset_id=asset_id,
            liability_id=liability_id,
            inflow_outflow_id=inflow_outflow_id,
            retirement_income_plan_id=retirement_income_plan_id
        )
        
        try:
            self.session.add(override)
            self.session.commit()
            return override
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create override", orig=e)

    def remove_override(self, override_id: int) -> bool:
        """
        Remove a specific override from a scenario.
        
        Args:
            override_id: ID of override to remove
            
        Returns:
            True if override was deleted, False if not found
        """
        stmt = delete(ScenarioOverride).where(ScenarioOverride.override_id == override_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def delete_scenario(self, scenario_id: int) -> bool:
        """
        Delete a scenario.
        
        Args:
            scenario_id: Primary key of scenario to delete
            
        Returns:
            True if scenario was deleted, False if not found
        """
        stmt = delete(Scenario).where(Scenario.scenario_id == scenario_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_scenario_summary(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of scenario information including override counts.
        
        Args:
            scenario_id: Primary key of scenario
            
        Returns:
            Dictionary containing scenario summary if found, None otherwise
        """
        scenario = self.get_scenario(scenario_id, include_assumptions=True, include_overrides=True)
        if not scenario:
            return None
            
        override_counts = {
            'asset_overrides': sum(1 for o in scenario.overrides if o.asset_id is not None),
            'liability_overrides': sum(1 for o in scenario.overrides if o.liability_id is not None),
            'cash_flow_overrides': sum(1 for o in scenario.overrides if o.inflow_outflow_id is not None),
            'retirement_income_overrides': sum(1 for o in scenario.overrides if o.retirement_income_plan_id is not None)
        }
            
        return {
            'scenario_id': scenario.scenario_id,
            'scenario_name': scenario.scenario_name,
            'plan_id': scenario.plan_id,
            'has_assumptions': scenario.assumptions is not None,
            'override_counts': override_counts,
            'created_at': scenario.created_at
        }