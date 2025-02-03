from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import Scenario, ScenarioAssumption, ScenarioOverride, Plan
from ..validation.money_validation import validate_positive_amount, validate_rate
from ..validation.time_validation import validate_year_range, validate_year_not_before_plan_creation

class ScenarioCRUD:
    """Handles CRUD operations for scenarios."""

    def __init__(self, session: Session):
        self.session = session

    def create_scenario(self, plan_id: int, scenario_name: str, scenario_color: Optional[str] = None,
                        assumptions: Optional[Dict[str, Any]] = None) -> Scenario:
        """Creates a scenario for a given plan."""
        # Get plan with base assumptions
        plan = self.session.execute(
            select(Plan)
            .options(joinedload(Plan.base_assumptions))
            .where(Plan.plan_id == plan_id)
        ).scalar_one_or_none()
        
        if not plan:
            raise NoResultFound(f"Plan {plan_id} not found")

        scenario = Scenario(plan_id=plan_id, scenario_name=scenario_name, scenario_color=scenario_color)

        try:
            self.session.add(scenario)
            self.session.flush()  # Get scenario_id

            # Clone base assumptions and merge with any provided overrides
            base_assumption_values = {}
            if plan.base_assumptions:
                base_assumption_values = {
                    'retirement_age_1': plan.base_assumptions.retirement_age_1,
                    'retirement_age_2': plan.base_assumptions.retirement_age_2,
                    'default_growth_rate': plan.base_assumptions.default_growth_rate,
                    'inflation_rate': plan.base_assumptions.inflation_rate
                }

            # Merge with provided assumptions
            if assumptions:
                base_assumption_values.update(assumptions)

            # Validate rates
            if 'default_growth_rate' in base_assumption_values:
                validate_rate(base_assumption_values['default_growth_rate'], "default_growth_rate")
            if 'inflation_rate' in base_assumption_values:
                validate_rate(base_assumption_values['inflation_rate'], "inflation_rate")
            if 'annual_retirement_spending' in base_assumption_values:
                validate_positive_amount(base_assumption_values['annual_retirement_spending'], "annual_retirement_spending")

            # Create scenario assumptions
            self.session.add(ScenarioAssumption(
                scenario_id=scenario.scenario_id,
                **base_assumption_values
            ))

            self.session.commit()
            return scenario

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create scenario", orig=e)

    def add_overrides(self, scenario_id: int, overrides: List[Dict[str, Any]]) -> List[ScenarioOverride]:
        """
        Bulk adds overrides for a scenario.
        
        overrides = [
            {
                'asset_id': 1,  # Optional - one of asset_id/liability_id/etc must be set
                'liability_id': None,
                'inflow_outflow_id': None,
                'retirement_income_plan_id': None,
                'override_field': 'value',  # What's being changed
                'override_value': '500000'  # New value
            },
            ...
        ]
        """
        scenario_overrides = []
        for override in overrides:
            if not any([override.get('asset_id'), override.get('liability_id'), 
                       override.get('inflow_outflow_id'), override.get('retirement_income_plan_id')]):
                raise ValueError("Override must have a valid target")
                
            scenario_override = ScenarioOverride(
                scenario_id=scenario_id,
                **override
            )
            self.session.add(scenario_override)
            scenario_overrides.append(scenario_override)
        
        try:
            self.session.commit()
            return scenario_overrides
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create overrides", orig=e)

    def add_override(self, scenario_id: int, override_field: str, override_value: str,
                     asset_id: Optional[int] = None, liability_id: Optional[int] = None,
                     inflow_outflow_id: Optional[int] = None, retirement_income_plan_id: Optional[int] = None) -> ScenarioOverride:
        """Adds an override to a scenario for a specific financial component."""
        if not any([asset_id, liability_id, inflow_outflow_id, retirement_income_plan_id]):
            raise ValueError("Override must have a valid target")

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

    def get_scenario(self, scenario_id: int, include_assumptions: bool = False, include_overrides: bool = False) -> Optional[Scenario]:
        """Retrieves a scenario by ID, optionally loading assumptions and overrides."""
        stmt = select(Scenario).where(Scenario.scenario_id == scenario_id)
        if include_assumptions:
            stmt = stmt.options(joinedload(Scenario.assumptions))
        if include_overrides:
            stmt = stmt.options(joinedload(Scenario.overrides))
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_scenarios(self, plan_id: int) -> List[Scenario]:
        """Returns all scenarios linked to a plan."""
        return list(self.session.execute(select(Scenario).where(Scenario.plan_id == plan_id)).scalars().all())

    def update_scenario(self, scenario_id: int, update_data: Dict[str, Any],
                        assumption_updates: Optional[Dict[str, Any]] = None) -> Optional[Scenario]:
        """Updates a scenario and its assumptions if provided."""
        try:
            scenario = self.session.execute(
                update(Scenario).where(Scenario.scenario_id == scenario_id).values(**update_data).returning(Scenario)
            ).scalar_one_or_none()
            if not scenario:
                return None

            if assumption_updates:
                if 'default_growth_rate' in assumption_updates:
                    validate_rate(assumption_updates['default_growth_rate'], "default_growth_rate")
                if 'inflation_rate' in assumption_updates:
                    validate_rate(assumption_updates['inflation_rate'], "inflation_rate")
                if 'annual_retirement_spending' in assumption_updates:
                    validate_positive_amount(assumption_updates['annual_retirement_spending'], "annual_retirement_spending")

                self.session.execute(update(ScenarioAssumption).where(ScenarioAssumption.scenario_id == scenario_id).values(**assumption_updates))

            self.session.commit()
            return scenario

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update scenario", orig=e)

    def update_override(self, override_id: int, override_field: str, override_value: str) -> Optional[ScenarioOverride]:
        """Updates an existing override's field and value."""
        try:
            result = self.session.execute(
                update(ScenarioOverride)
                .where(ScenarioOverride.override_id == override_id)
                .values(override_field=override_field, override_value=override_value)
                .returning(ScenarioOverride)
            )
            self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update override", orig=e)

    def remove_override(self, override_id: int) -> bool:
        """Deletes a specific scenario override."""
        result = self.session.execute(delete(ScenarioOverride).where(ScenarioOverride.override_id == override_id))
        self.session.commit()
        return result.rowcount > 0

    def delete_scenario(self, scenario_id: int) -> bool:
        """Deletes a scenario by ID."""
        result = self.session.execute(delete(Scenario).where(Scenario.scenario_id == scenario_id))
        self.session.commit()
        return result.rowcount > 0

    def get_scenario_summary(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """Returns a summary of a scenario, including override counts."""
        scenario = self.get_scenario(scenario_id, include_assumptions=True, include_overrides=True)
        if not scenario:
            return None

        return {
            'scenario_id': scenario.scenario_id,
            'scenario_name': scenario.scenario_name,
            'plan_id': scenario.plan_id,
            'has_assumptions': scenario.assumptions is not None,
            'override_counts': {
                'asset_overrides': sum(1 for o in scenario.overrides if o.asset_id),
                'liability_overrides': sum(1 for o in scenario.overrides if o.liability_id),
                'cash_flow_overrides': sum(1 for o in scenario.overrides if o.inflow_outflow_id),
                'retirement_income_overrides': sum(1 for o in scenario.overrides if o.retirement_income_plan_id)
            },
            'created_at': scenario.created_at
        }