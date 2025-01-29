# FIPly README: Financial Independence Projection Tool

Overview
FIPly is a HIGHLY FLEXIBLE Financial Independence Projection tool designed specifically for financial advisors. It runs locally on a private company server (no security, authentication, or other considerations are required). Built with Python, SQLite, and SQLAlchemy, FIPly empowers advisors to create detailed financial plans, model complex what-if scenarios, and provide actionable insights to their clients. The system is tailored for maximum flexibility.

Core Features
Households
Households are the starting point of the app, storing client data and serving as the foundation for financial planning.

Each household can have multiple plans, allowing advisors to model strategies for different financial stages or goals.
Plans
Plans represent the core financial structure for a household.

Each household can have multiple plans associated with it.
Plans begin as a blank slate unless duplicated from an existing plan.
Plans can be duplicated to allow advisors a starting point if they desire.
Plans are comprised of base facts and scenarios.

Base facts are flexible and can be updated at any time, impacting all scenarios that reference them (unless overridden in a scenario).
Base Facts
Base facts define a household’s financial reality and are stored at the plan level. They include:

Assets: Values, ownership, growth rates (default, custom, or stepwise), and nest egg inclusion.
Liabilities: Values, interest rates, ownership, and nest egg inclusion.
Inflows and Outflows: Recurring income or expenses with start and end dates, annual amounts, and a toggle for inflation.
Retirement Income Plans: Sources like Social Security or pensions with start/end ages, amounts, and nest egg inclusion.
Global Assumptions: Retirement ages, inflation rates, final ages, and default growth rate.
Base facts serve as the foundation for scenarios but are not tied to static values. If an advisor updates base facts, those changes will apply to all scenarios still referencing them unless specific overrides have been applied.

Scenarios
Scenarios allow advisors to create what-if models by duplicating the base facts of a plan and customizing them.

Scenarios start as a copy of the base facts and can be adjusted independently through overrides.
Scenarios do not modify the original base facts and instead allow for flexible testing of different strategies.
Customizable Elements for Scenarios
Advisors can override nearly any input or parameter from the base facts. Examples include:

Adding, removing, or modifying assets, liabilities, inflows, and outflows.
Adjusting ownership, values, or nest egg inclusion for assets or liabilities.
Changing growth rates for individual components:
Default growth rates.
Custom growth rates.
Stepwise growth rates, with gaps defaulting to the global rate.
Modifying retirement ages for either or both individuals.
Adding or removing inflows and outflows with inflation toggles.
Adjusting default growth rates at the scenario level.
Setting annual retirement spending, which drives scenario projections.
Retirement Spending in Scenarios
Retirement spending is intentionally omitted from base facts. Advisors experiment with annual spending amounts directly in scenarios to test their impact on portfolio longevity. If advisors want to apply retirement spending to the base facts, they can simply create a new scenario and adjust the spending value there.

Growth Rate Configuration
The app’s growth rate system offers three levels of customization, with growth rates linked directly to specific components (e.g., assets or retirement income plans):

Default Growth Rate: A global growth rate applied to all applicable components unless explicitly overridden.
Custom Growth Rates: Assigned to specific assets or retirement income plans for unique assumptions.
Stepwise Growth Rates: Configured for specific time periods, with gaps automatically defaulting to the global growth rate.
Growth rates are stored with explicit references to the related components, ensuring referential integrity. Advisors can adjust growth rates at the scenario level, enabling precise modeling for time-sensitive or asset-specific growth projections.

Retirement Nest Egg
The app allows advisors to toggle whether specific assets or liabilities are included in the retirement nest egg, which serves as the basis for retirement projections.

The toggle lets advisors exclude assets or liabilities irrelevant to retirement, such as:
Properties not intended for sale.
Liabilities expected to be paid off before retirement.
Other financial components irrelevant to retirement, etc.
Nest egg inclusion is scenario-specific, allowing advisors to test different retirement strategies while preserving net worth calculations for a comprehensive financial picture.

Database Schema
Standard Formatting Practices
Text: Used for names, descriptions, and identifiers.
Monetary Values: Stored as REAL with two decimal places.
Percentages: Stored as decimals (e.g., 0.05 for 5%).
Booleans: Represented as INTEGER (0 for FALSE, 1 for TRUE).
Dates: Stored in ISO 8601 format (YYYY-MM-DD).
Ages: Stored as INTEGER (67, 34, etc.).
Foreign Keys: Use ON DELETE CASCADE to maintain referential integrity.
Database Design Principles
Growth rate configurations and scenario overrides reference components like assets or liabilities through explicit columns (asset_id, liability_id, etc.).
Referential integrity is enforced through foreign key constraints, ensuring no invalid references.
Indexes are used for commonly queried fields to optimize performance.

— Date / Age handling for this app:
Store dates of birth as DATE and ages as INTEGER for data integrity. Dynamically calculate age and dates as needed to ensure accuracy and flexibility. This minimizes redundancy, keeps the schema clean, and ensures derived values are always up-to-date.


The database schema supports FIPly’s functionality efficiently and includes tables for:  
- Households: Core client data.  
- Plans: High-level financial strategies tied to households.  
- Base Assumptions: Global parameters for plans, such as retirement ages, inflation rates, and growth rates.



# SQLite SCHEMA

```
-- This schema follows standard formatting best practices:
-- - Dates are stored in ISO 8601 format (YYYY-MM-DD).
-- - Boolean values are represented as INTEGER (0 for FALSE, 1 for TRUE).
-- - Text fields are used for names, descriptions, and identifiers.
-- - Foreign key relationships use ON DELETE CASCADE to maintain referential integrity.
-- - Monetary values and amounts are stored as REAL with a precision of two decimal places.
-- - Percentages (e.g., growth rates) are stored as REAL and expressed as decimals (e.g., 0.05 for 5%).

-- HOUSEHOLDS TABLE
-- Stores basic client information, serving as the primary organizational unit.
CREATE TABLE households (
    household_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each household
    household_name TEXT NOT NULL,                    -- Name of the household
    person1_first_name TEXT NOT NULL,                -- First name of Person 1
    person1_last_name TEXT NOT NULL,                 -- Last name of Person 1
    person1_dob DATE NOT NULL,                       -- Date of birth for Person 1
    person2_first_name TEXT,                         -- First name of Person 2 (optional)
    person2_last_name TEXT,                          -- Last name of Person 2 (optional)
    person2_dob DATE,                                -- Date of birth for Person 2 (optional)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of when the household was created
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP    -- Timestamp of the last update
);

-- PLANS TABLE
-- Represents financial plans associated with a household.
CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Unique identifier for each plan
    household_id INTEGER NOT NULL,                   -- Reference to the household this plan belongs to
    plan_name TEXT NOT NULL,                         -- Name of the plan
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of when the plan was created
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of the last update
    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE
);

-- BASE ASSUMPTIONS TABLE
-- Stores global assumptions for each plan, such as retirement ages and growth rates.
CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,                     -- One-to-one relationship with the plan
    retirement_age_1 INTEGER,                        -- Retirement age for Person 1
    retirement_age_2 INTEGER,                        -- Retirement age for Person 2
    final_age_1 INTEGER,                             -- Planning horizon (final age) for Person 1
    final_age_2 INTEGER,                             -- Planning horizon (final age) for Person 2
    final_age_selector INTEGER,                      -- Which person's final age is used (1 or 2)
    default_growth_rate REAL,                        -- Default growth rate applied to assets/liabilities
    inflation_rate REAL,                             -- Assumed inflation rate
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- SCENARIOS TABLE
-- Represents what-if scenarios associated with a plan.
CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique identifier for each scenario
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this scenario belongs to
    scenario_name TEXT NOT NULL,                     -- Name of the scenario
    scenario_color TEXT,                             -- Optional color for visualization in charts
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of when the scenario was created
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- SCENARIO ASSUMPTIONS TABLE
-- Stores high-level scenario-specific assumptions that override base assumptions.
CREATE TABLE scenario_assumptions (
    scenario_id INTEGER PRIMARY KEY,                 -- One-to-one relationship with the scenario
    retirement_age_1 INTEGER,                        -- Scenario-specific retirement age for Person 1
    retirement_age_2 INTEGER,                        -- Scenario-specific retirement age for Person 2
    default_growth_rate REAL,                        -- Scenario-specific default growth rate
    inflation_rate REAL,                             -- Scenario-specific inflation rate
    annual_retirement_spending REAL,                 -- Annual retirement spending specific to the scenario
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);

-- SCENARIO OVERRIDES TABLE
-- Stores granular overrides for financial components within scenarios.
CREATE TABLE scenario_overrides (
    override_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique identifier for each override
    scenario_id INTEGER NOT NULL,                    -- Reference to the scenario this override belongs to
    asset_id INTEGER,                                -- Reference to an asset (if overriding an asset)
    liability_id INTEGER,                            -- Reference to a liability (if overriding a liability)
    inflow_outflow_id INTEGER,                       -- Reference to an inflow/outflow (if overriding one)
    retirement_income_plan_id INTEGER,               -- Reference to a retirement income plan (if overriding one)
    override_field TEXT NOT NULL,                    -- Field being overridden (e.g., 'value', 'growth_rate')
    override_value TEXT NOT NULL,                    -- New value for the field
    
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
-- Stores customizable categories for organizing assets.
CREATE TABLE asset_categories (
    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each category
    plan_id INTEGER NOT NULL,                            -- Reference to the plan this category belongs to
    category_name TEXT NOT NULL,                         -- Name of the category
    category_order INTEGER DEFAULT 0,                    -- Optional order for displaying categories
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- ASSETS TABLE
-- Represents assets associated with a plan, with optional categories and growth rates.
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Unique identifier for each asset
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this asset belongs to
    asset_category_id INTEGER NOT NULL,              -- Reference to the category this asset belongs to
    asset_name TEXT NOT NULL,                        -- Name of the asset
    owner TEXT NOT NULL,                             -- Ownership type
    value REAL NOT NULL,                             -- Current value of the asset
    include_in_nest_egg INTEGER DEFAULT 1,           -- Whether the asset is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
);

-- LIABILITY CATEGORIES TABLE
-- Stores customizable categories for organizing liabilities.
CREATE TABLE liability_categories (
    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each category
    plan_id INTEGER NOT NULL,                                -- Reference to the plan this category belongs to
    category_name TEXT NOT NULL,                             -- Name of the category
    category_order INTEGER DEFAULT 0,                        -- Optional order for displaying categories
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- LIABILITIES TABLE
-- Represents liabilities associated with a plan, with optional categories and interest rates.
CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each liability
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this liability belongs to
    liability_category_id INTEGER NOT NULL,          -- Reference to the category this liability belongs to
    liability_name TEXT NOT NULL,                    -- Name of the liability
    owner TEXT NOT NULL,                             -- Ownership type
    value REAL NOT NULL,                             -- Current value of the liability
    interest_rate REAL,                              -- Optional interest rate for the liability
    include_in_nest_egg INTEGER DEFAULT 1,           -- Whether the liability is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
);

-- INFLOWS AND OUTFLOWS TABLE
-- Represents recurring cash flows (income or expenses) associated with a plan.
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each inflow or outflow
    plan_id INTEGER NOT NULL,                            -- Reference to the plan this cash flow belongs to
    type TEXT NOT NULL,                                  -- Whether it is an inflow or outflow
    name TEXT NOT NULL,                                  -- Name of the inflow or outflow
    annual_amount REAL NOT NULL,                         -- Annual amount of the cash flow
    start_date DATE NOT NULL,                            -- Start date of the cash flow
    end_date DATE,                                       -- End date of the cash flow
    apply_inflation INTEGER DEFAULT 0,                   -- Whether inflation is applied to the cash flow
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- RETIREMENT INCOME PLANS TABLE
-- Represents retirement income sources such as Social Security or pensions.
CREATE TABLE retirement_income_plans (
    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each income plan
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this income plan belongs to
    name TEXT NOT NULL,                              -- Name of the income source
    owner TEXT NOT NULL,                             -- Ownership type
    annual_income REAL NOT NULL,                     -- Annual income amount
    start_age INTEGER NOT NULL,                      -- Age when income starts
    end_age INTEGER,                                 -- Age when income ends (optional)
    include_in_nest_egg INTEGER DEFAULT 1,           -- Whether the income is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- GROWTH RATE CONFIGURATIONS TABLE
-- Centralized table for managing default, custom, and stepwise growth rates.
CREATE TABLE growth_rate_configurations (
    growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each growth rate configuration
    asset_id INTEGER,                                 -- Reference to an asset (if configuring asset growth)
    retirement_income_plan_id INTEGER,                -- Reference to a retirement income plan (if configuring income growth)
    scenario_id INTEGER,                              -- Reference to the scenario (if scenario-specific)
    configuration_type TEXT NOT NULL,                 -- 'DEFAULT', 'OVERRIDE', or 'STEPWISE'
    start_date DATE,                                  -- Start date for stepwise growth rates
    end_date DATE,                                    -- End date for stepwise growth rates
    growth_rate REAL NOT NULL,                        -- Growth rate value

    FOREIGN KEY (asset_id)
        REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (retirement_income_plan_id)
        REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id)
        REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);

-- INDEXES

-- Indexes for HOUSEHOLDS
CREATE INDEX idx_households_name ON households (household_name);

-- Indexes for PLANS
CREATE INDEX idx_plans_household_id ON plans (household_id);

-- Indexes for SCENARIOS
CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id);

-- Indexes for SCENARIO OVERRIDES
CREATE INDEX idx_scenario_overrides_scenario_id ON scenario_overrides (scenario_id);
CREATE INDEX idx_scenario_overrides_asset_id ON scenario_overrides (asset_id);
CREATE INDEX idx_scenario_overrides_liability_id ON scenario_overrides (liability_id);
CREATE INDEX idx_scenario_overrides_inflow_outflow_id ON scenario_overrides (inflow_outflow_id);
CREATE INDEX idx_scenario_overrides_rip_id ON scenario_overrides (retirement_income_plan_id);

-- Indexes for ASSET CATEGORIES
CREATE INDEX idx_asset_categories_plan_id ON asset_categories (plan_id);

-- Indexes for ASSETS
CREATE INDEX idx_assets_plan_id ON assets (plan_id);
CREATE INDEX idx_assets_category_id ON assets (asset_category_id);

-- Indexes for LIABILITY CATEGORIES
CREATE INDEX idx_liability_categories_plan_id ON liability_categories (plan_id);

-- Indexes for LIABILITIES
CREATE INDEX idx_liabilities_plan_id ON liabilities (plan_id);
CREATE INDEX idx_liabilities_category_id ON liabilities (liability_category_id);

-- Indexes for INFLOWS AND OUTFLOWS
CREATE INDEX idx_inflows_outflows_plan_id ON inflows_outflows (plan_id);
CREATE INDEX idx_inflows_outflows_type ON inflows_outflows (type);

-- Indexes for RETIREMENT INCOME PLANS
CREATE INDEX idx_retirement_income_plans_plan_id ON retirement_income_plans (plan_id);

-- Indexes for GROWTH RATE CONFIGURATIONS
CREATE INDEX idx_growth_rate_configurations_asset_id ON growth_rate_configurations (asset_id);
CREATE INDEX idx_growth_rate_configurations_rip_id ON growth_rate_configurations (retirement_income_plan_id);
CREATE INDEX idx_growth_rate_configurations_scenario_id ON growth_rate_configurations (scenario_id);
CREATE INDEX idx_growth_rate_configurations_dates ON growth_rate_configurations (start_date, end_date);```


