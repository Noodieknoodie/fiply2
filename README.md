# MOTTO: "store what you know, calculate what you need." : Let the backend handle any necessary conversions between these formats based on the specific needs of the application.

# FIPly README: Financial Independence Projection Tool

## Overview
FIPly is a **highly structured** financial independence projection tool designed for financial advisors. It runs locally on a private company server, eliminating the need for security, authentication, or external connectivity considerations. Built with **Python, SQLite, and SQLAlchemy**, FIPly enables advisors to create structured financial plans, model flexible what-if scenarios, and provide actionable insights to their clients. The system is streamlined for efficiency and accuracy.

## Core Features
### Households
Households are the starting point of the app, storing client data and serving as the foundation for financial planning. Each household can contain multiple plans, allowing advisors to structure strategies for different financial objectives.

### Plans
Plans represent a household’s **core financial framework**. Each plan is an independent model containing base financial facts and multiple scenarios.

- Each household can have multiple plans, each functioning independently.
- Plans start as a structured framework and can be duplicated to facilitate scenario comparisons.
- Plans consist of **base facts** and **scenarios**.

### Base Facts
Base facts define a household’s financial landscape and are stored at the plan level. They include:

- **Assets**: Values, ownership, and whether they contribute to the retirement nest egg.
- **Liabilities**: Debt amounts, interest rates, ownership, and nest egg inclusion.
- **Inflows and Outflows**: Income and expenses, stored with **annual amounts** and applicable start/end years.
- **Retirement Income Plans**: Sources such as Social Security or pensions, stored with start/end ages, annual values, and nest egg inclusion settings.
- **Global Assumptions**: Retirement ages, inflation rates, and default growth rates.

Base facts function as a foundation for all scenarios within a plan but can be adjusted within scenarios as needed without modifying the original data.

### Scenarios
Scenarios allow advisors to model different financial strategies by duplicating the base facts and customizing them. These act as **alternative projections** that do not impact the original plan data.

- Scenarios begin as a copy of the base facts and allow independent adjustments.
- Advisors can override nearly any financial input for comparative modeling.
- Modifications do not alter the base facts, ensuring the ability to return to the original assumptions if needed.

### Customizable Elements for Scenarios
Advisors can override nearly any financial assumption, including:

- Adding, removing, or modifying **assets, liabilities, and cash flows**.
- Adjusting **ownership, values, and nest egg inclusion** for assets or liabilities.
- Modifying growth rates:
  - Default global growth rates
  - Custom growth rates for specific assets or income sources
  - Stepwise growth rates for period-specific adjustments
- Adjusting **retirement ages and final ages**
- Adding or removing inflows and outflows with **inflation adjustments**
- Modifying **annual retirement spending**, which directly impacts nest egg projections

### Retirement Spending in Scenarios
Retirement spending is handled **directly in scenarios** rather than in base facts. This ensures that financial advisors can test different retirement spending levels without impacting the foundational household data. If an advisor wants to create a baseline spending assumption, they can do so within a specific scenario.

### Growth Rate Configuration
The system offers **structured growth rate management**, ensuring clear and predictable modeling:

- **Default Growth Rate**: A single global rate applies unless overridden.
- **Custom Growth Rates**: Applied to specific assets or income sources.
- **Stepwise Growth Rates**: Defined for specific timeframes, with gaps defaulting to the global rate.

Growth rates are **explicitly linked** to assets or income streams, ensuring referential integrity and precise modeling.

### Retirement Nest Egg
The **retirement nest egg** is the core value tracked for financial independence projections. Advisors can **toggle inclusion/exclusion** for any asset or liability to refine nest egg calculations.

- **Included Assets**: Those contributing to retirement funding.
- **Excluded Assets**: Non-liquid or non-retirement assets, such as real estate not intended for sale.
- **Excluded Liabilities**: Debts expected to be repaid before retirement.

Nest egg calculations are **scenario-specific**, enabling financial advisors to test different strategies while maintaining an accurate view of net worth.

## Database Schema
### Standard Formatting Practices
- **Text**: Used for names, descriptions, and identifiers.
- **Monetary Values**: Stored as REAL with two decimal places.
- **Percentages**: Stored as decimals (e.g., 0.05 for 5%).
- **Booleans**: Stored as INTEGER (0 for FALSE, 1 for TRUE).
- **Years**: Stored as INTEGER (e.g., 2025).
- **Ages**: Stored as INTEGER (e.g., 65).
- **Foreign Keys**: Enforce referential integrity using ON DELETE CASCADE.

### Date & Age Handling
- **Birthdates** are stored as DATE for reference but are primarily used to derive ages dynamically.
- **Financial events are stored using age-based logic**, ensuring structured planning independent of specific calendar dates.
- **Inflation and growth adjustments** occur at the start of each financial year to maintain consistency.

## Summary
FIPly is a **structured, forward-looking** financial projection tool designed to streamline financial modeling while maintaining flexibility. By separating **base facts and scenarios**, it allows advisors to explore multiple financial paths while preserving an accurate and clean data model. The system’s **focus on nest egg trajectory rather than detailed cash flow tracking** ensures clarity and usability for long-term planning.




# **FIPLI: BUSINESS LOGIC**  

FIPLI is a financial projection tool designed for financial advisors to model long-term financial scenarios for client households. A **household** contains multiple **plans**, and each plan contains multiple **scenarios**, allowing advisors to create “what-if” projections by modifying base assumptions without altering core plan data. The system operates **linearly** without Monte Carlo simulations and focuses purely on **forward-looking asset trajectory modeling**.  

FIPLI differs from conventional financial planning software by **eliminating unnecessary complexity** while maintaining projection accuracy. Instead of tracking income, expenses, and withdrawals in detail, FIPLI models all financial events as adjustments to a single **nest egg trajectory**—which includes all assets and liabilities combined. **Retirement spending is a single planned outflow**, modifying the nest egg directly rather than tracking how expenses are covered by specific income or assets.  

### **Key Principles & Differentiators**  
1. **Time is measured in ages and years, not specific dates, but precise data should be stored when known.** The system operates on age increments rather than calendar dates for simplicity but maintains accuracy by storing full birthdates for future reference.  
2. **All financial events apply at the start of the year.** This includes inflows (income, inheritances, asset sales), planned spending (retirement withdrawals), and investment growth. There is no intra-year cash flow tracking.  
3. **Inflation applies at the start of the year before modifying values.** This ensures consistency when adjusting inflows, outflows, and asset growth projections.  
4. **Growth is applied annually before retirement spending.** Asset appreciation is factored in before deducting planned spending, ensuring a consistent year-over-year accumulation model.  
5. **Debt balances accrue interest annually, but debt payments are not tracked.** Net worth growth naturally accounts for liability management without explicit debt servicing logic.  
6. **Lump sum inflows (inheritance, asset sales) apply at the start of the year and immediately adjust the nest egg.** These are not treated as separate income streams but as instant asset increases.  
7. **No logic for "covering expenses" from income or withdrawals.** Unlike traditional tools, FIPLI does not match expenses against specific income sources. Instead, retirement spending reduces the nest egg directly, maintaining a clear projection trajectory.  

### **Schema Adjustments**  
- **Birthdates (DATE) should be stored in full** to preserve known information. However, calculations should primarily use birth years for age-based modeling.  
- **Years (INTEGER) should be used** when planning future financial events rather than specific dates.  
- **Ages (INTEGER) remain the primary method** of time-based financial logic, ensuring a simplified approach while maintaining the ability to derive precise values when necessary.  

---  

# **SINGLE SOURCE OF TRUTH**  

1. **Events apply at the start of the year** unless explicitly marked otherwise.  
2. **Ages increment at the beginning of the year.**  
3. **Growth is applied at the start of the year.**  
4. **Inflation applies at the start of the year before modifying projected values.**  
5. **Income and inflows (salary, pensions, rental income, etc.) are added at the start of the year.**  
6. **Projected retirement spending is a single planned outflow entry that adjusts the nest egg trajectory.**  
7. **Retirement spending is deducted at the start of the year before applying growth.**  
8. **There is no logic for “covering” expenses—spending simply lowers the nest egg according to the projection.**  
9. **Debt interest accrues annually at the start of the year.** No explicit payments are tracked; net worth growth accounts for liability management.  
10. **Lump sum inflows (inheritances, asset sales) are applied at the start of the year and factored into the nest egg immediately.**  
11. **The priority order for financial events within a year is:**  
    - **(1) Apply inflows (income, inheritances, lump sums)**  
    - **(2) Apply inflation adjustments**  
    - **(3) Deduct retirement spending**  
    - **(4) Apply investment growth**  

This structure ensures that **all assets, liabilities, and financial events contribute to a single, unified projection** while preserving accuracy by storing known data while computing based on simplified metrics.




########
SCHEMA: backend\database_operations\database\fiply2_database.db
########

-- SCHEMA OVERVIEW AND CONVENTIONS
-- This schema uses natural "source of truth" metrics for all time-based fields:
-- - Exact dates (DATE) for known dates like birthdates
-- - Ages (INTEGER) for age-based events like retirement
-- - Years (INTEGER) for future events and market projections
-- Other conventions:
-- - Boolean values stored as INTEGER (0 for FALSE, 1 for TRUE)
-- - Monetary values stored as REAL with 2 decimal precision
-- - Growth rates and percentages stored as REAL decimal (0.05 for 5%)
-- - All tables include appropriate foreign keys with ON DELETE CASCADE

-- HOUSEHOLDS TABLE
-- Primary organizational unit storing client information
CREATE TABLE households (
    household_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_name TEXT NOT NULL,
    person1_first_name TEXT NOT NULL,
    person1_last_name TEXT NOT NULL,
    person1_dob DATE NOT NULL,                      -- Full date for precise calculations
    person2_first_name TEXT,
    person2_last_name TEXT,
    person2_dob DATE,                               -- Full date for precise calculations
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PLANS TABLE
-- Financial plans associated with a household
CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE
);

-- BASE ASSUMPTIONS TABLE
-- Global assumptions for each plan
CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,
    retirement_age_1 INTEGER,                       -- Age-based: "Retire at 65"
    retirement_age_2 INTEGER,                       -- Age-based: "Retire at 65"
    final_age_1 INTEGER,                           -- Age-based: "Plan until 95"
    final_age_2 INTEGER,                           -- Age-based: "Plan until 95"
    final_age_selector INTEGER,                     -- Which person's final age to use (1 or 2)
    default_growth_rate REAL,                      -- Annual growth rate (e.g., 0.05 for 5%)
    inflation_rate REAL,                           -- Annual inflation rate (e.g., 0.03 for 3%)
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- SCENARIOS TABLE
-- What-if scenarios for different planning approaches
CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_name TEXT NOT NULL,
    scenario_color TEXT,                            -- For UI visualization
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- SCENARIO ASSUMPTIONS TABLE
-- Scenario-specific overrides of base assumptions
CREATE TABLE scenario_assumptions (
    scenario_id INTEGER PRIMARY KEY,
    retirement_age_1 INTEGER,                       -- Age-based: Retirement planning is age-focused
    retirement_age_2 INTEGER,                       -- Age-based: Retirement planning is age-focused
    default_growth_rate REAL,                      -- Annual rate
    inflation_rate REAL,                           -- Annual rate
    annual_retirement_spending REAL,                -- Amount
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);

-- SCENARIO OVERRIDES TABLE
-- Granular overrides for specific components within scenarios
CREATE TABLE scenario_overrides (
    override_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    asset_id INTEGER,                               -- Optional: if overriding an asset
    liability_id INTEGER,                           -- Optional: if overriding a liability
    inflow_outflow_id INTEGER,                      -- Optional: if overriding a cash flow
    retirement_income_plan_id INTEGER,              -- Optional: if overriding retirement income
    override_field TEXT NOT NULL,                   -- Field being overridden
    override_value TEXT NOT NULL,                   -- New value (matches source table's format)
    
    FOREIGN KEY (scenario_id) 
        REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) 
        REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_id) 
        REFERENCES liabilities (liability_id) ON DELETE CASCADE,
    FOREIGN KEY (inflow_outflow_id) 
        REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE,
    FOREIGN KEY (retirement_income_plan_id)
        REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE
);

-- ASSET CATEGORIES TABLE
-- Organizational categories for assets
CREATE TABLE asset_categories (
    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    category_order INTEGER DEFAULT 0,               -- For UI ordering
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- ASSETS TABLE
-- All assets associated with a plan
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    asset_category_id INTEGER NOT NULL,
    asset_name TEXT NOT NULL,
    owner TEXT NOT NULL,                           -- 'person1', 'person2', or 'joint'
    value REAL NOT NULL,                          -- Current value
    include_in_nest_egg INTEGER DEFAULT 1,        -- Include in retirement calculations
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
);

-- LIABILITY CATEGORIES TABLE
-- Organizational categories for liabilities
CREATE TABLE liability_categories (
    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    category_order INTEGER DEFAULT 0,               -- For UI ordering
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- LIABILITIES TABLE
-- All liabilities/debts associated with a plan
CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    liability_category_id INTEGER NOT NULL,
    liability_name TEXT NOT NULL,
    owner TEXT NOT NULL,                           -- 'person1', 'person2', or 'joint'
    value REAL NOT NULL,                          -- Current value
    interest_rate REAL,                           -- Annual interest rate
    include_in_nest_egg INTEGER DEFAULT 1,        -- Include in retirement calculations
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
);

-- INFLOWS AND OUTFLOWS TABLE
-- Regular cash flows (income/expenses)
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    type TEXT NOT NULL,                           -- 'inflow' or 'outflow'
    name TEXT NOT NULL,
    owner TEXT NOT NULL,                          -- 'person1', 'person2', or 'joint'
    annual_amount REAL NOT NULL,
    start_year INTEGER NOT NULL,                  -- Year-based: "Inheritance in 2025"
    end_year INTEGER,                             -- Year-based: "Until 2030"
    apply_inflation INTEGER DEFAULT 0,            -- Should amount inflate over time?
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- RETIREMENT INCOME PLANS TABLE
-- Retirement income sources (Social Security, pensions, etc.)
CREATE TABLE retirement_income_plans (
    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,                          -- 'person1', 'person2', or 'joint'
    annual_income REAL NOT NULL,
    start_age INTEGER NOT NULL,                   -- Age-based: "Social Security at 67"
    end_age INTEGER,                              -- Age-based: "Pension until 85"
    include_in_nest_egg INTEGER DEFAULT 1,        -- Include in retirement calculations
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- GROWTH RATE CONFIGURATIONS TABLE
-- Manages growth rates for assets and income sources
CREATE TABLE growth_rate_configurations (
    growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,                               -- Optional: if configuring asset growth
    retirement_income_plan_id INTEGER,              -- Optional: if configuring income growth
    scenario_id INTEGER,                            -- Optional: if scenario-specific
    configuration_type TEXT NOT NULL,               -- 'DEFAULT', 'OVERRIDE', or 'STEPWISE'
    start_year INTEGER NOT NULL,                    -- Year-based: Market projections by year
    end_year INTEGER,                               -- Year-based: Market projections by year
    growth_rate REAL NOT NULL,                      -- Annual rate
    
    FOREIGN KEY (asset_id)
        REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (retirement_income_plan_id)
        REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id)
        REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);

-- INDEXES
-- Optimizing common queries and relationships

-- Households
CREATE INDEX idx_households_name ON households (household_name);

-- Plans
CREATE INDEX idx_plans_household_id ON plans (household_id);

-- Scenarios
CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id);

-- Scenario Overrides
CREATE INDEX idx_scenario_overrides_scenario_id ON scenario_overrides (scenario_id);
CREATE INDEX idx_scenario_overrides_asset_id ON scenario_overrides (asset_id);
CREATE INDEX idx_scenario_overrides_liability_id ON scenario_overrides (liability_id);
CREATE INDEX idx_scenario_overrides_inflow_outflow_id ON scenario_overrides (inflow_outflow_id);
CREATE INDEX idx_scenario_overrides_rip_id ON scenario_overrides (retirement_income_plan_id);

-- Asset Categories
CREATE INDEX idx_asset_categories_plan_id ON asset_categories (plan_id);

-- Assets
CREATE INDEX idx_assets_plan_id ON assets (plan_id);
CREATE INDEX idx_assets_category_id ON assets (asset_category_id);

-- Liability Categories
CREATE INDEX idx_liability_categories_plan_id ON liability_categories (plan_id);

-- Liabilities
CREATE INDEX idx_liabilities_plan_id ON liabilities (plan_id);
CREATE INDEX idx_liabilities_category_id ON liabilities (liability_category_id);

-- Inflows and Outflows
CREATE INDEX idx_inflows_outflows_plan_id ON inflows_outflows (plan_id);
CREATE INDEX idx_inflows_outflows_type ON inflows_outflows (type);
CREATE INDEX idx_inflows_outflows_years ON inflows_outflows (start_year, end_year);

-- Retirement Income Plans
CREATE INDEX idx_retirement_income_plans_plan_id ON retirement_income_plans (plan_id);

-- Growth Rate Configurations
CREATE INDEX idx_growth_rate_configurations_asset_id ON growth_rate_configurations (asset_id);
CREATE INDEX idx_growth_rate_configurations_rip_id ON growth_rate_configurations (retirement_income_plan_id);
CREATE INDEX idx_growth_rate_configurations_scenario_id ON growth_rate_configurations (scenario_id);
CREATE INDEX idx_growth_rate_configurations_years ON growth_rate_configurations (start_year, end_year);