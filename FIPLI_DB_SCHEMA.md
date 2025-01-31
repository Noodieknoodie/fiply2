backend\database_operations\database\fiply2_database.db

# This document contains the schema preview for the FIPLI database.

################ FIPLI: DB Schema #################

DB File Path: backend\database_operations\database\fiply2_database.db


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