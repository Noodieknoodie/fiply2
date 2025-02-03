# backend/database_operations/crud/scenarios.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import Scenario, ScenarioAssumption, ScenarioOverride, Plan
from ..validation.money_validation import validate_positive_amount, validate_rate

class ScenarioCRUD:
    """Handles CRUD operations for scenarios."""

    def __init__(self, session: Session):
        self.session = session

    def create_scenario(self, plan_id: int, scenario_name: str, scenario_color: Optional[str] = None,
                        assumptions: Optional[Dict[str, Any]] = None) -> Scenario:
        """Creates a scenario for a given plan."""
        if not self.session.execute(select(Plan).where(Plan.plan_id == plan_id)).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} not found")

        scenario = Scenario(plan_id=plan_id, scenario_name=scenario_name, scenario_color=scenario_color)

        try:
            self.session.add(scenario)
            self.session.flush()

            if assumptions:
                if 'default_growth_rate' in assumptions:
                    validate_rate(assumptions['default_growth_rate'], "default_growth_rate")
                if 'inflation_rate' in assumptions:
                    validate_rate(assumptions['inflation_rate'], "inflation_rate")
                if 'annual_retirement_spending' in assumptions:
                    validate_positive_amount(assumptions['annual_retirement_spending'], "annual_retirement_spending")

                self.session.add(ScenarioAssumption(scenario_id=scenario.scenario_id, **assumptions))

            self.session.commit()
            return scenario

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create scenario", orig=e)

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

    def add_override(self, scenario_id: int, override_field: str, override_value: str,
                     asset_id: Optional[int] = None, liability_id: Optional[int] = None,
                     inflow_outflow_id: Optional[int] = None, retirement_income_plan_id: Optional[int] = None) -> ScenarioOverride:
        """Adds an override to a scenario for a specific financial component."""
        if not any([asset_id, liability_id, inflow_outflow_id, retirement_income_plan_id]):
            raise ValueError("Override must have a valid target")

        override = ScenarioOverride(
            scenario_id=scenario_id, override_field=override_field, override_value=override_value,
            asset_id=asset_id, liability_id=liability_id, inflow_outflow_id=inflow_outflow_id,
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
