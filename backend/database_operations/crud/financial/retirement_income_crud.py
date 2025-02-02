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
    """CRUD operations for retirement income plan management."""
    
    def __init__(self, session: Session):
        self.session = session

    def create_retirement_income(
        self,
        plan_id: int,
        name: str,
        owner: str,
        annual_income: float,
        start_age: int,
        end_age: Optional[int] = None,
        include_in_nest_egg: bool = True,
        apply_inflation: bool = False,
        growth_config: Optional[Dict[str, Any]] = None
    ) -> RetirementIncomePlan:
        """
        Create a new retirement income plan.
        
        Args:
            plan_id: ID of plan this income belongs to
            name: Name identifier for the income (e.g., "Social Security")
            owner: Owner of the income ('person1', 'person2', or 'joint')
            annual_income: Annual amount of income
            start_age: Age when income begins
            end_age: Optional age when income ends
            include_in_nest_egg: Whether to include in retirement calculations
            apply_inflation: Whether to apply inflation adjustments
            growth_config: Optional growth rate configuration
            
        Returns:
            Newly created RetirementIncomePlan instance
            
        Raises:
            ValueError: If validation fails
            NoResultFound: If plan_id doesn't exist
            IntegrityError: If database constraint violated
        """
        # Verify plan exists
        stmt = select(Plan).where(Plan.plan_id == plan_id)
        plan = self.session.execute(stmt).scalar_one_or_none()
        if not plan:
            raise NoResultFound(f"Plan {plan_id} not found")

        # Validate input
        validate_positive_amount(annual_income, "annual_income")
        
        if owner not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        # Validate age sequence if end_age provided
        if end_age is not None:
            if not validate_age_sequence(start_age, start_age, end_age):
                raise ValueError("Start age must be before or equal to end age")

        # Create retirement income instance
        income_plan = RetirementIncomePlan(
            plan_id=plan_id,
            name=name,
            owner=owner,
            annual_income=annual_income,
            start_age=start_age,
            end_age=end_age,
            include_in_nest_egg=include_in_nest_egg,
            apply_inflation=apply_inflation
        )
        
        try:
            self.session.add(income_plan)
            self.session.flush()  # Get income_plan_id without committing

            # Add growth configuration if provided
            if growth_config:
                self._add_growth_configuration(income_plan.income_plan_id, growth_config)

            self.session.commit()
            return income_plan

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to create retirement income plan", orig=e)

    def get_retirement_income(
        self,
        income_id: int,
        include_growth_config: bool = False
    ) -> Optional[RetirementIncomePlan]:
        """
        Retrieve a retirement income plan by ID.
        
        Args:
            income_id: Primary key of income plan
            include_growth_config: If True, eagerly loads growth configuration
            
        Returns:
            RetirementIncomePlan instance if found, None otherwise
        """
        stmt = select(RetirementIncomePlan).where(
            RetirementIncomePlan.income_plan_id == income_id
        )
        
        if include_growth_config:
            stmt = stmt.options(joinedload(RetirementIncomePlan.growth_rates))
            
        return self.session.execute(stmt).scalar_one_or_none()

    def get_plan_retirement_income(
        self,
        plan_id: int,
        owner: Optional[str] = None
    ) -> List[RetirementIncomePlan]:
        """
        Retrieve all retirement income plans for a plan, optionally filtered by owner.
        
        Args:
            plan_id: ID of plan to get income plans for
            owner: Optional owner to filter by
            
        Returns:
            List of RetirementIncomePlan instances
        """
        stmt = select(RetirementIncomePlan).where(
            RetirementIncomePlan.plan_id == plan_id
        )
        
        if owner:
            stmt = stmt.where(RetirementIncomePlan.owner == owner)
            
        return list(self.session.execute(stmt).scalars().all())

    def update_retirement_income(
        self,
        income_id: int,
        update_data: Dict[str, Any],
        growth_config: Optional[Dict[str, Any]] = None
    ) -> Optional[RetirementIncomePlan]:
        """
        Update a retirement income plan.
        
        Args:
            income_id: Primary key of income plan to update
            update_data: Dictionary of fields to update and their new values
            growth_config: Optional new growth rate configuration
            
        Returns:
            Updated RetirementIncomePlan instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraint violated
        """
        # Validate amount if included in update
        if 'annual_income' in update_data:
            validate_positive_amount(update_data['annual_income'], "annual_income")

        # Validate owner if included
        if 'owner' in update_data and update_data['owner'] not in ['person1', 'person2', 'joint']:
            raise ValueError("Invalid owner value")

        # Validate age sequence if updating ages
        if 'start_age' in update_data or 'end_age' in update_data:
            current_income = self.get_retirement_income(income_id)
            if not current_income:
                return None
                
            start_age = update_data.get('start_age', current_income.start_age)
            end_age = update_data.get('end_age', current_income.end_age)
            
            if end_age is not None and not validate_age_sequence(start_age, start_age, end_age):
                raise ValueError("Start age must be before or equal to end age")

        try:
            # Update income plan
            stmt = (
                update(RetirementIncomePlan)
                .where(RetirementIncomePlan.income_plan_id == income_id)
                .values(**update_data)
                .returning(RetirementIncomePlan)
            )
            result = self.session.execute(stmt)
            income_plan = result.scalar_one_or_none()
            
            if not income_plan:
                return None

            # Update growth configuration if provided
            if growth_config:
                # Remove existing configuration
                stmt = delete(GrowthRateConfiguration).where(
                    GrowthRateConfiguration.retirement_income_plan_id == income_id
                )
                self.session.execute(stmt)
                
                # Add new configuration
                self._add_growth_configuration(income_id, growth_config)

            self.session.commit()
            return income_plan

        except IntegrityError as e:
            self.session.rollback()
            raise IntegrityError("Failed to update retirement income plan", orig=e)

    def delete_retirement_income(self, income_id: int) -> bool:
        """
        Delete a retirement income plan.
        
        Args:
            income_id: Primary key of income plan to delete
            
        Returns:
            True if income plan was deleted, False if not found
        """
        stmt = delete(RetirementIncomePlan).where(
            RetirementIncomePlan.income_plan_id == income_id
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def _add_growth_configuration(
        self,
        income_id: int,
        config: Dict[str, Any]
    ) -> None:
        """
        Add growth rate configuration for a retirement income plan.
        
        Args:
            income_id: ID of income plan to configure
            config: Growth configuration dictionary
            
        Raises:
            ValueError: If validation fails
        """
        validate_rate(config.get('growth_rate'), "growth_rate")
        
        growth_config = GrowthRateConfiguration(
            retirement_income_plan_id=income_id,
            configuration_type='OVERRIDE',
            start_year=config.get('start_year'),
            end_year=config.get('end_year'),
            growth_rate=config.get('growth_rate')
        )
        self.session.add(growth_config)

    def get_retirement_income_summary(
        self,
        income_id: int,
        include_years: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get a summary of retirement income information.
        
        Args:
            income_id: Primary key of income plan
            include_years: If True, includes calculated start/end years
            
        Returns:
            Dictionary containing income summary if found, None otherwise
        """
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
            # Note: Actual year calculation would be done in calculation layer
            summary.update({
                'duration': (income.end_age - income.start_age + 1) if income.end_age else None,
                'is_lifetime': income.end_age is None
            })

        return summary

    def get_total_retirement_income(
        self,
        plan_id: int,
        age: int,
        include_in_nest_egg_only: bool = False
    ) -> float:
        """
        Calculate total retirement income at a specific age.
        
        Args:
            plan_id: ID of plan to calculate total for
            age: Age to calculate total for
            include_in_nest_egg_only: If True, only sum income marked for nest egg
            
        Returns:
            Total annual income from all matching retirement income plans
        """
        stmt = select(RetirementIncomePlan).where(
            RetirementIncomePlan.plan_id == plan_id,
            RetirementIncomePlan.start_age <= age
        )
        
        if include_in_nest_egg_only:
            stmt = stmt.where(RetirementIncomePlan.include_in_nest_egg == True)
            
        income_plans = self.session.execute(stmt).scalars().all()
        
        total = 0.0
        for plan in income_plans:
            if plan.end_age is None or plan.end_age >= age:
                total += plan.annual_income
                
        return total