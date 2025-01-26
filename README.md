# README

---

Fiply is a robust yet user-friendly Financial Independence Projection tool built with Python and SQL on the backend and React for the front end. It is specifically designed for Financial Advisors, not the general population, to create detailed financial projections tailored to their clients' unique situations. This tool empowers advisors to model and simulate potential financial scenarios, helping clients make informed decisions about savings strategies, real estate transactions, growth rate adjustments, retirement planning, and other key financial events.

---

### Base Facts
Base facts are the foundation of the financial plan. Advisors input all key financial data and assumptions for a household, including:
- **Assets**: Their values, ownership, growth rates, and toggles for inclusion in the retirement nest egg.
- **Liabilities**: Their values, interest rates, ownership, and toggles for inclusion in the retirement nest egg.
- **Inflows and Outflows**: Recurring income or expenses with parameters like start and end dates, annual amounts, and a toggle for applying inflation.
- **Retirement Income Plans**: Sources like Social Security, pensions, or other defined benefits, with their start and end ages, annual amounts, and toggles for inclusion in the retirement nest egg.
- **Global Assumptions**: Default growth rates, inflation rates, retirement ages, and final planning ages.

The base facts represent the household’s current financial reality and long-term assumptions. They act as the starting point for projections and analyses.

---

### What-If Scenarios
From the base facts, advisors can create any number of **what-if scenarios** to explore alternative financial outcomes. Each scenario starts as an exact duplication of the base facts but can be customized through **overrides**, allowing advisors to change almost any input or parameter. This flexibility lets advisors model both simple and complex situations, such as:

- **Simple Overrides**:
  - Adjusting the default growth rate.
  - Excluding a liability or asset from the retirement nest egg.
  - Changing the start or end date of a recurring inflow or outflow.

- **Complex Scenarios**:
  - Changing retirement start dates for one or both household members.
  - Adding or removing assets or liabilities.
  - Applying stepwise growth rates to specific financial components.
  - Adjusting retirement spending levels to reflect different lifestyle choices, etc.

Each scenario acts as an independent layer that overlays the base facts, enabling advisors to compare different strategies side by side. The base facts remain intact for reference, ensuring clarity and consistency.

---

### Growth Rate Configuration
A standout feature of Fiply is its **multi-tiered growth rate configuration system**, giving advisors complete flexibility to model various financial assumptions:
1. **Default Growth Rate**:
   - Applied globally across all assets or liabilities unless overridden.
2. **Custom Growth Rates**:
   - Assigned to specific assets or liabilities to reflect unique growth assumptions.
3. **Stepwise Growth Rates**:
   - Configured to change over time, with unique rates for defined periods (e.g., 2025-2030 at 5%, 2031-2040 at 7%). Any gaps in time automatically default to the global growth rate.

Advisors can make growth rate adjustments directly within scenarios, enabling even more precise modeling of future outcomes.

---

### Nest Egg Inclusion Toggle
Fiply allows advisors to **toggle whether specific assets or liabilities are included in the retirement nest egg**, which serves as the foundation for retirement projections. While all assets and liabilities are automatically included in the **net worth calculation** (representing the household’s full financial picture), the nest egg toggle enables advisors to exclude items like:
- Properties not intended for sale.
- Liabilities expected to be paid off before retirement.
- Any other financial component deemed irrelevant to retirement calculations, etc.

This ensures retirement projections focus only on the assets and liabilities relevant to retirement, while net worth remains comprehensive.

---

Fiply is a tool designed for efficiency, clarity, and flexibility. By organizing financial data into base facts and scenarios, and enabling powerful customization options like growth rate configurations and retirement toggles, advisors can provide their clients with deep insights into their financial futures while modeling a wide range of possibilities.


---

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
    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE -- Cascades delete
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
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
);

-- SCENARIOS TABLE
-- Represents what-if scenarios associated with a plan.
CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique identifier for each scenario
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this scenario belongs to
    scenario_name TEXT NOT NULL,                     -- Name of the scenario
    scenario_color TEXT,                             -- Optional color for visualization in charts
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- Timestamp of when the scenario was created
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
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
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE -- Cascades delete
);

-- SCENARIO OVERRIDES TABLE
-- Stores granular overrides for financial components (e.g., assets, liabilities) within scenarios.
CREATE TABLE scenario_overrides (
    override_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique identifier for each override
    scenario_id INTEGER NOT NULL,                    -- Reference to the scenario this override belongs to
    base_fact_type TEXT NOT NULL,                    -- Type of base fact being overridden (e.g., 'ASSET', 'LIABILITY')
    base_fact_id INTEGER NOT NULL,                   -- ID of the specific base fact being overridden
    override_field TEXT NOT NULL,                    -- Field being overridden (e.g., 'value', 'growth_rate')
    override_value TEXT NOT NULL,                    -- New value for the field
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE -- Cascades delete
);

-- ASSET CATEGORIES TABLE
-- Stores customizable categories for organizing assets.
CREATE TABLE asset_categories (
    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each category
    plan_id INTEGER NOT NULL,                            -- Reference to the plan this category belongs to
    category_name TEXT NOT NULL,                         -- Name of the category
    category_order INTEGER DEFAULT 0,                    -- Optional order for displaying categories
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
);

-- ASSETS TABLE
-- Represents assets associated with a plan, with optional categories and growth rates.
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Unique identifier for each asset
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this asset belongs to
    asset_category_id INTEGER NOT NULL,              -- Reference to the category this asset belongs to
    asset_name TEXT NOT NULL,                        -- Name of the asset
    owner TEXT CHECK (owner IN ('Person 1', 'Person 2', 'Joint')) NOT NULL, -- Ownership type
    value REAL NOT NULL,                             -- Current value of the asset
    include_in_nest_egg BOOLEAN DEFAULT TRUE,        -- Whether the asset is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE, -- Cascades delete
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE -- Cascades delete
);

-- LIABILITY CATEGORIES TABLE
-- Stores customizable categories for organizing liabilities.
CREATE TABLE liability_categories (
    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each category
    plan_id INTEGER NOT NULL,                                -- Reference to the plan this category belongs to
    category_name TEXT NOT NULL,                             -- Name of the category
    category_order INTEGER DEFAULT 0,                        -- Optional order for displaying categories
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
);

-- LIABILITIES TABLE
-- Represents liabilities associated with a plan, with optional categories and interest rates.
CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each liability
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this liability belongs to
    liability_category_id INTEGER NOT NULL,          -- Reference to the category this liability belongs to
    liability_name TEXT NOT NULL,                    -- Name of the liability
    owner TEXT CHECK (owner IN ('Person 1', 'Person 2', 'Joint')) NOT NULL, -- Ownership type
    value REAL NOT NULL,                             -- Current value of the liability
    interest_rate REAL,                              -- Optional interest rate for the liability
    include_in_nest_egg BOOLEAN DEFAULT TRUE,        -- Whether the liability is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE, -- Cascades delete
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE -- Cascades delete
);

-- INFLOWS AND OUTFLOWS TABLE
-- Represents recurring cash flows (income or expenses) associated with a plan.
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each inflow or outflow
    plan_id INTEGER NOT NULL,                            -- Reference to the plan this cash flow belongs to
    type TEXT CHECK (type IN ('INFLOW', 'OUTFLOW')) NOT NULL, -- Whether it is an inflow or outflow
    name TEXT NOT NULL,                                  -- Name of the inflow or outflow
    annual_amount REAL NOT NULL,                         -- Annual amount of the cash flow
    start_date DATE NOT NULL,                            -- Start date of the cash flow
    end_date DATE,                                       -- End date of the cash flow
    apply_inflation BOOLEAN DEFAULT FALSE,               -- Whether inflation is applied to the cash flow
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
);

-- RETIREMENT INCOME PLANS TABLE
-- Represents retirement income sources such as Social Security or pensions.
CREATE TABLE retirement_income_plans (
    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each income plan
    plan_id INTEGER NOT NULL,                        -- Reference to the plan this income plan belongs to
    name TEXT NOT NULL,                              -- Name of the income source
    owner TEXT CHECK (owner IN ('Person 1', 'Person 2', 'Joint')) NOT NULL, -- Ownership type
    annual_income REAL NOT NULL,                     -- Annual income amount
    start_age INTEGER NOT NULL,                      -- Age when income starts
    end_age INTEGER,                                 -- Age when income ends (optional)
    include_in_nest_egg BOOLEAN DEFAULT TRUE,        -- Whether the income is included in retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE -- Cascades delete
);

-- GROWTH RATE CONFIGURATIONS TABLE
-- Centralized table for managing default, custom, and stepwise growth rates.
CREATE TABLE growth_rate_configurations (
    growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each growth rate configuration
    entity_type TEXT NOT NULL,                        -- Type of entity (e.g., 'ASSET', 'RETIREMENT_INCOME')
    entity_id INTEGER NOT NULL,                       -- Reference to the specific entity this growth rate applies to
    scenario_id INTEGER,                              -- Reference to the scenario this growth rate applies to (if applicable)
    configuration_type TEXT NOT NULL,                 -- 'DEFAULT', 'OVERRIDE', or 'STEPWISE'
    start_date DATE,                                  -- Start date for stepwise growth rates
    end_date DATE,                                    -- End date for stepwise growth rates
    growth_rate REAL NOT NULL,                        -- Growth rate value
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) -- Cascades delete
);

-- Indexes for HOUSEHOLDS
CREATE INDEX idx_households_name ON households (household_name);

-- Indexes for PLANS
CREATE INDEX idx_plans_household_id ON plans (household_id);

-- Indexes for BASE ASSUMPTIONS
-- No additional indexes needed as plan_id is the primary key.

-- Indexes for SCENARIOS
CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id);

-- Indexes for SCENARIO ASSUMPTIONS
-- No additional indexes needed as scenario_id is the primary key.

-- Indexes for SCENARIO OVERRIDES
CREATE INDEX idx_scenario_overrides_scenario_id ON scenario_overrides (scenario_id);
CREATE INDEX idx_scenario_overrides_base_fact_id ON scenario_overrides (base_fact_id);

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
CREATE INDEX idx_growth_rate_configurations_entity ON growth_rate_configurations (entity_type, entity_id);
CREATE INDEX idx_growth_rate_configurations_scenario_id ON growth_rate_configurations (scenario_id);
CREATE INDEX idx_growth_rate_configurations_dates ON growth_rate_configurations (start_date, end_date);
```

---

### Below is an example of how the schema can handle asset growth rate configurations and scenario adjustments.

The situation is as follows: three assets are added to the base facts of a financial plan, each with different growth rate configurations:

1. Asset 1 is set to the default growth rate of 6%, inherited from `base_assumptions`.
2. Asset 2 is assigned a custom growth rate of 10%, stored in `growth_rate_configurations` with `configuration_type = 'OVERRIDE'`.
3. Asset 3 is assigned a stepwise growth rate:
   - 3% from 2026-01-01 to 2033-01-01.
   - 4% from 2040-01-01 to 2045-01-01.
   - 20% from 2050-01-01 to 2052-01-01.
   - For all other periods, the default growth rate (6%) applies.

How the Schema Handles the Base Facts:
- Asset 1 has no entry in `growth_rate_configurations` since it defaults to the global growth rate.
- Asset 2 has a single entry in `growth_rate_configurations` with its custom 10% rate.
- Asset 3 has multiple entries in `growth_rate_configurations`, each specifying a time range and growth rate for its stepwise configuration.

---

Now a scenario is created that inherits all base facts, and the growth rates for the three assets are modified as follows:

1. Asset 1 is changed to a custom growth rate of 8%.
2. Asset 2 is updated to a stepwise growth rate:
   - 5% from 2026-01-01 to 2030-01-01.
   - 7% from 2035-01-01 to 2040-01-01.
   - The default growth rate (6%) applies outside these periods.
3. Asset 3 has its stepwise growth rates adjusted:
   - 4.5% from 2026-01-01 to 2033-01-01.
   - 5% from 2040-01-01 to 2046-01-01.
   - 22% from 2050-01-01 to 2055-01-01.

How the Schema Handles the Scenario Adjustments:
- For Asset 1, a new entry is added to `growth_rate_configurations` with the scenario ID and the 8% rate.
- For Asset 2, multiple stepwise entries are created in `growth_rate_configurations` under the scenario ID.
- For Asset 3, new stepwise entries replace the inherited ones under the scenario ID.

The schema ensures that:
- All scenario-specific changes are linked to the scenario ID in `growth_rate_configurations`.
- Default growth rates are applied only when no custom or stepwise rates exist for a given period.
- The base facts remain unchanged, allowing for easy comparisons between scenarios.


### Below is an example of how the schema can handle retirement spending, liabilities, and inflows, along with their scenario adjustments.

The situation is as follows: a financial plan is created with the following base facts:

1. Annual retirement spending is set to $50,000, stored in `base_assumptions`.
2. A liability for a mortgage is added with:
   - Value: $200,000.
   - Interest rate: 3.5%.
   - Included in the retirement nest egg (default).
3. An inflow from rental income is added with:
   - Annual amount: $24,000.
   - Start date: 2025-01-01.
   - End date: 2035-12-31.
   - Inflation is applied.

How the Schema Handles the Base Facts:
- Retirement spending is stored in `base_assumptions` under `annual_retirement_spending`.
- The mortgage is added to the `liabilities` table with its value, interest rate, and inclusion in the nest egg.
- Rental income is stored in the `inflows_outflows` table, with flags for inflation and specific start and end dates.

---

Now a scenario is created that inherits all base facts, and the following adjustments are made:

1. Annual retirement spending is increased to $60,000 for this scenario.
2. The mortgage is excluded from the retirement nest egg to test the impact of paying it off before retirement.
3. Rental income is extended to 2040-12-31 and adjusted to $30,000 annually, with inflation still applied.

How the Schema Handles the Scenario Adjustments:
- Retirement spending is updated in the `scenario_assumptions` table for this scenario, leaving the base assumption intact.
- The mortgage is adjusted in the `scenario_overrides` table, setting the `include_in_nest_egg` flag to `FALSE` for this liability.
- Rental income is updated in the `scenario_overrides` table with:
   - New end date: 2040-12-31.
   - New annual amount: $30,000.

The schema ensures that:
- Adjustments specific to the scenario are stored in `scenario_assumptions` and `scenario_overrides`, leaving the base facts untouched.
- Inflation continues to be applied to the rental income because the flag is inherited from the base fact unless explicitly changed.
- The scenario accurately reflects changes to spending, liabilities, and inflows for comparison with the base plan or other scenarios.


### THESE ARE JUST A FEW RANDOM SCENARIOS — IN REALITY, THE FLEXIBILITY OF THE SCHEMA ALLOWS FOR NEARLY ANY COMBINATION OF ADJUSTMENTS, INCLUDING CHANGES TO ASSETS, LIABILITIES, SPENDING, INCOME, OR GROWTH CONFIGURATIONS. ADVISORS CAN BUILD, TEST, AND COMPARE COMPLEX FINANCIAL STRATEGIES WHILE KEEPING THE BASE PLAN INTACT, AS THE FOUNDATION TO ALL SCENARIOS CREATED ###
