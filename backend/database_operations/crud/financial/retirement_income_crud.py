# backend/database_operations/crud/financial/retirement.py
"""
Full CRUD operations for retirement income following SQLAlchemy 2.0 style
Support for optional growth rate configuration
Proper validation of:
Income amounts (positive)
Owner values
Age sequence
Support for:
Filtering by owner
Inflation toggle
Nest egg inclusion/exclusion
Optional end age
Comprehensive income summary including:
Duration calculation
Lifetime income detection
Growth rate presence
Additional utility for calculating total income at specific age
Proper error handling and transaction management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from ...models import RetirementIncomePlan, Plan, GrowthRateConfiguration
from ...validation.money_validation import validate_positive_amount, validate_rate
from ...validation.time_validation import validate_age_sequence


class RetirementIncomeCRUD:
    """Handles CRUD operations for retirement income plans."""

    def __init__(self, session: Session):
        self.session = session

    def create_retirement_income(self, plan_id: int, name: str, owner: str, annual_income: float, start_age: int,
                                 end_age: Optional[int] = None, include_in_nest_egg: bool = True,
                                 apply_inflation: bool = False, growth_config: Optional[Dict[str, Any]] = None) -> RetirementIncomePlan:
        """Creates a retirement income plan."""
        if not self.session.execute(select(Plan).where(Plan.plan_id == plan_id)).scalar_one_or_none():
            raise NoResultFound(f"Plan {plan_id} not found")

        validate_positive_amount(annual_income, "annual_income")
        if owner not in {"person1", "person2", "joint"}:
            raise ValueError("Invalid owner value")

        if end_age is not None and not validate_age_sequence(start_age, start_age, end_age):
            raise ValueError("Start age must be before or equal to end age")

        income_plan = RetirementIncomePlan(
            plan_id=plan_id, name=name, owner=owner, annual_income=annual_income, start_age=start_age,
            end_age=end_age, include_in_nest_egg=include_in_nest_egg, apply_inflation=apply_inflation
        )

        try:
            self.session.add(income_plan)
            self.session.flush()

            if growth_config:
                self._add_growth_configuration(income_plan.income_plan_id, growth_config)

            self.session.commit()
            return income_plan
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create retirement income plan", orig=e)

    def get_retirement_income(self, income_id: int, include_growth_config: bool = False) -> Optional[RetirementIncomePlan]:
        """Retrieves a retirement income plan by ID."""
        stmt = select(RetirementIncomePlan).where(RetirementIncomePlan.income_plan_id == income_id)
        if include_growth_config:
            stmt = stmt.options(joinedload(RetirementIncomePlan.growth_rates))
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_retirement_income(self, plan_id: int, owner: Optional[str] = None) -> List[RetirementIncomePlan]:
        """Returns all retirement income plans for a plan, optionally filtered by owner."""
        stmt = select(RetirementIncomePlan).where(RetirementIncomePlan.plan_id == plan_id)
        if owner:
            stmt = stmt.where(RetirementIncomePlan.owner == owner)
        return list(self.session.execute(stmt).scalars().all())

    def update_retirement_income(self, income_id: int, update_data: Dict[str, Any],
                                 growth_config: Optional[Dict[str, Any]] = None) -> Optional[RetirementIncomePlan]:
        """Updates a retirement income plan."""
        if 'annual_income' in update_data:
            validate_positive_amount(update_data['annual_income'], "annual_income")

        if 'owner' in update_data and update_data['owner'] not in {"person1", "person2", "joint"}:
            raise ValueError("Invalid owner value")

        if 'start_age' in update_data or 'end_age' in update_data:
            current_income = self.get_retirement_income(income_id)
            if not current_income:
                return None

            start_age = update_data.get('start_age', current_income.start_age)
            end_age = update_data.get('end_age', current_income.end_age)

            if end_age is not None and not validate_age_sequence(start_age, start_age, end_age):
                raise ValueError("Start age must be before or equal to end age")

        try:
            stmt = update(RetirementIncomePlan).where(RetirementIncomePlan.income_plan_id == income_id).values(**update_data).returning(RetirementIncomePlan)
            result = self.session.execute(stmt)
            income_plan = result.scalar_one_or_none()

            if not income_plan:
                return None

            if growth_config:
                self.session.execute(delete(GrowthRateConfiguration).where(GrowthRateConfiguration.retirement_income_plan_id == income_id))
                self._add_growth_configuration(income_id, growth_config)

            self.session.commit()
            return income_plan
        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update retirement income plan", orig=e)

    def delete_retirement_income(self, income_id: int) -> bool:
        """Deletes a retirement income plan."""
        result = self.session.execute(delete(RetirementIncomePlan).where(RetirementIncomePlan.income_plan_id == income_id))
        self.session.commit()
        return result.rowcount > 0

    def _add_growth_configuration(self, income_id: int, config: Dict[str, Any]) -> None:
        """Adds a growth rate configuration for a retirement income plan."""
        validate_rate(config.get('growth_rate'), "growth_rate")

        self.session.add(GrowthRateConfiguration(
            retirement_income_plan_id=income_id, configuration_type='OVERRIDE',
            start_year=config.get('start_year'), end_year=config.get('end_year'), growth_rate=config.get('growth_rate')
        ))

    def get_retirement_income_summary(self, income_id: int, include_years: bool = False) -> Optional[Dict[str, Any]]:
        """Returns a summary of a retirement income plan."""
        income = self.get_retirement_income(income_id, include_growth_config=True)
        if not income:
            return None

        summary = {
            'income_id': income.income_plan_id,
            'name': income.name,
            'owner': income.owner,
            'annual_income': income.annual_income,
            'start_age': income.start_age,
            'end_age': income.end_age,
            'include_in_nest_egg': income.include_in_nest_egg,
            'apply_inflation': income.apply_inflation,
            'has_growth_rate': bool(income.growth_rates)
        }

        if include_years:
            summary.update({
                'duration': (income.end_age - income.start_age + 1) if income.end_age else None,
                'is_lifetime': income.end_age is None
            })

        return summary

    def get_total_retirement_income(self, plan_id: int, age: int, include_in_nest_egg_only: bool = False) -> float:
        """Calculates total retirement income at a specific age."""
        stmt = select(RetirementIncomePlan).where(RetirementIncomePlan.plan_id == plan_id, RetirementIncomePlan.start_age <= age)
        if include_in_nest_egg_only:
            stmt = stmt.where(RetirementIncomePlan.include_in_nest_egg.is_(True))

        income_plans = self.session.execute(stmt).scalars().all()

        return sum(plan.annual_income for plan in income_plans if plan.end_age is None or plan.end_age >= age)
