from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

class Household(Base):
    """Represents a household in the financial planning system."""
    __tablename__ = "households"
    
    household_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_name: Mapped[str] = mapped_column(Text, nullable=False)
    person1_first_name: Mapped[str] = mapped_column(Text, nullable=False)
    person1_last_name: Mapped[str] = mapped_column(Text, nullable=False)
    person1_dob: Mapped[date] = mapped_column(Date, nullable=False)
    person2_first_name: Mapped[Optional[str]] = mapped_column(Text)
    person2_last_name: Mapped[Optional[str]] = mapped_column(Text)
    person2_dob: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    plans: Mapped[List["Plan"]] = relationship(back_populates="household", cascade="all, delete-orphan")

class Plan(Base):
    """Financial plan model."""
    __tablename__ = "plans"

    plan_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.household_id", ondelete="CASCADE"), nullable=False)
    plan_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    household: Mapped["Household"] = relationship("Household", back_populates="plans")
    base_assumptions: Mapped[Optional["BaseAssumption"]] = relationship(
        back_populates="plan", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    scenarios: Mapped[List["Scenario"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan"
    )
    asset_categories: Mapped[List["AssetCategory"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    liability_categories: Mapped[List["LiabilityCategory"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    assets: Mapped[List["Asset"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    liabilities: Mapped[List["Liability"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    inflows_outflows: Mapped[List["InflowOutflow"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )
    retirement_income_plans: Mapped[List["RetirementIncomePlan"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan"
    )

class BaseAssumption(Base):
    """Stores global assumptions for a plan."""
    __tablename__ = "base_assumptions"
    
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), primary_key=True)
    retirement_age_1: Mapped[Optional[int]] = mapped_column(Integer)
    retirement_age_2: Mapped[Optional[int]] = mapped_column(Integer)
    final_age_1: Mapped[Optional[int]] = mapped_column(Integer)
    final_age_2: Mapped[Optional[int]] = mapped_column(Integer)
    final_age_selector: Mapped[Optional[int]] = mapped_column(Integer)
    default_growth_rate: Mapped[Optional[float]] = mapped_column(Float)
    inflation_rate: Mapped[Optional[float]] = mapped_column(Float)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="base_assumptions")

class Scenario(Base):
    """Represents a what-if scenario for a plan."""
    __tablename__ = "scenarios"
    
    scenario_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    scenario_name: Mapped[str] = mapped_column(Text, nullable=False)
    scenario_color: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="scenarios")
    assumptions: Mapped[Optional["ScenarioAssumption"]] = relationship(
        back_populates="scenario", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    overrides: Mapped[List["ScenarioOverride"]] = relationship(
        back_populates="scenario", 
        cascade="all, delete-orphan"
    )
    growth_rates: Mapped[List["GrowthRateConfiguration"]] = relationship(
        back_populates="scenario", 
        cascade="all, delete-orphan"
    )

class ScenarioAssumption(Base):
    """Stores scenario-specific assumptions."""
    __tablename__ = "scenario_assumptions"
    
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.scenario_id", ondelete="CASCADE"), primary_key=True)
    retirement_age_1: Mapped[Optional[int]] = mapped_column(Integer)
    retirement_age_2: Mapped[Optional[int]] = mapped_column(Integer)
    default_growth_rate: Mapped[Optional[float]] = mapped_column(Float)
    inflation_rate: Mapped[Optional[float]] = mapped_column(Float)
    annual_retirement_spending: Mapped[Optional[float]] = mapped_column(Float)

    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="assumptions")

class ScenarioOverride(Base):
    """Stores granular overrides for financial components within scenarios."""
    __tablename__ = "scenario_overrides"
    
    override_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.scenario_id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.asset_id", ondelete="CASCADE"))
    liability_id: Mapped[Optional[int]] = mapped_column(ForeignKey("liabilities.liability_id", ondelete="CASCADE"))
    inflow_outflow_id: Mapped[Optional[int]] = mapped_column(ForeignKey("inflows_outflows.inflow_outflow_id", ondelete="CASCADE"))
    retirement_income_plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("retirement_income_plans.income_plan_id", ondelete="CASCADE"))
    override_field: Mapped[str] = mapped_column(Text, nullable=False)
    override_value: Mapped[str] = mapped_column(Text, nullable=False)

    scenario = relationship("Scenario", back_populates="overrides")
    asset = relationship("Asset", back_populates="overrides")
    liability = relationship("Liability", back_populates="overrides")
    inflow_outflow = relationship("InflowOutflow", back_populates="overrides")
    retirement_income_plan = relationship("RetirementIncomePlan", back_populates="overrides")

class AssetCategory(Base):
    """Represents categories for organizing assets."""
    __tablename__ = "asset_categories"
    
    asset_category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    category_order: Mapped[int] = mapped_column(Integer, default=0)

    plan = relationship("Plan", back_populates="asset_categories")
    assets = relationship("Asset", back_populates="category")

class Asset(Base):
    """Represents assets associated with a plan."""
    __tablename__ = "assets"
    
    asset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    asset_category_id: Mapped[int] = mapped_column(ForeignKey("asset_categories.asset_category_id", ondelete="CASCADE"), nullable=False)
    asset_name: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False)  # 'person1', 'person2', or 'joint'
    value: Mapped[float] = mapped_column(Float, nullable=False)
    include_in_nest_egg: Mapped[bool] = mapped_column(Boolean, default=True)

    plan = relationship("Plan", back_populates="assets")
    category = relationship("AssetCategory", back_populates="assets")
    overrides = relationship("ScenarioOverride", back_populates="asset")
    growth_rates = relationship("GrowthRateConfiguration", back_populates="asset")

class LiabilityCategory(Base):
    """Represents categories for organizing liabilities."""
    __tablename__ = "liability_categories"
    
    liability_category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    category_order: Mapped[int] = mapped_column(Integer, default=0)

    plan = relationship("Plan", back_populates="liability_categories")
    liabilities = relationship("Liability", back_populates="category")

class Liability(Base):
    """Represents liabilities associated with a plan."""
    __tablename__ = "liabilities"
    
    liability_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    liability_category_id: Mapped[int] = mapped_column(ForeignKey("liability_categories.liability_category_id", ondelete="CASCADE"), nullable=False)
    liability_name: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False)  # 'person1', 'person2', or 'joint'
    value: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[Optional[float]] = mapped_column(Float)
    include_in_nest_egg: Mapped[bool] = mapped_column(Boolean, default=True)

    plan = relationship("Plan", back_populates="liabilities")
    category = relationship("LiabilityCategory", back_populates="liabilities")
    overrides = relationship("ScenarioOverride", back_populates="liability")

class InflowOutflow(Base):
    """Represents recurring cash flows (income or expenses)."""
    __tablename__ = "inflows_outflows"
    
    inflow_outflow_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)  # 'inflow' or 'outflow'
    name: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False)  # 'person1', 'person2', or 'joint'
    annual_amount: Mapped[float] = mapped_column(Float, nullable=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[Optional[int]] = mapped_column(Integer)
    apply_inflation: Mapped[bool] = mapped_column(Boolean, default=False)

    plan = relationship("Plan", back_populates="inflows_outflows")
    overrides = relationship("ScenarioOverride", back_populates="inflow_outflow")

class RetirementIncomePlan(Base):
    """Represents retirement income sources like Social Security or pensions."""
    __tablename__ = "retirement_income_plans"
    
    income_plan_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.plan_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False)  # 'person1', 'person2', or 'joint'
    annual_income: Mapped[float] = mapped_column(Float, nullable=False)
    start_age: Mapped[int] = mapped_column(Integer, nullable=False)
    end_age: Mapped[Optional[int]] = mapped_column(Integer)
    include_in_nest_egg: Mapped[bool] = mapped_column(Boolean, default=True)
    apply_inflation: Mapped[bool] = mapped_column(Boolean, default=False)

    plan = relationship("Plan", back_populates="retirement_income_plans")
    overrides = relationship("ScenarioOverride", back_populates="retirement_income_plan")
    growth_rates = relationship("GrowthRateConfiguration", back_populates="retirement_income_plan")

class GrowthRateConfiguration(Base):
    """Manages growth rates for assets and retirement income plans."""
    __tablename__ = "growth_rate_configurations"
    
    growth_rate_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.asset_id", ondelete="CASCADE"))
    retirement_income_plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("retirement_income_plans.income_plan_id", ondelete="CASCADE"))
    scenario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("scenarios.scenario_id", ondelete="CASCADE"))
    configuration_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'DEFAULT', 'OVERRIDE', or 'STEPWISE'
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[Optional[int]] = mapped_column(Integer)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)

    asset = relationship("Asset", back_populates="growth_rates")
    retirement_income_plan = relationship("RetirementIncomePlan", back_populates="growth_rates")
    scenario = relationship("Scenario", back_populates="growth_rates")

# Create all tables in the engine
from .connection import engine
Base.metadata.create_all(bind=engine)
