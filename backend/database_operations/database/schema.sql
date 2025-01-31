BEGIN TRANSACTION;
CREATE TABLE asset_categories (

    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    category_name TEXT NOT NULL,

    category_order INTEGER DEFAULT 0,               -- For UI ordering

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);
INSERT INTO "asset_categories" VALUES(1,1,'Real Estate',1);
INSERT INTO "asset_categories" VALUES(2,1,'Retirement Accounts',2);
INSERT INTO "asset_categories" VALUES(3,1,'Investments',3);
INSERT INTO "asset_categories" VALUES(4,2,'Tech Stocks',1);
INSERT INTO "asset_categories" VALUES(5,2,'Crypto',2);
INSERT INTO "asset_categories" VALUES(6,2,'Index Funds',3);
INSERT INTO "asset_categories" VALUES(7,2,'Real Estate',4);
INSERT INTO "asset_categories" VALUES(8,6,'International Real Estate',1);
INSERT INTO "asset_categories" VALUES(9,6,'Global Equities',2);
INSERT INTO "asset_categories" VALUES(10,6,'Cryptocurrency',3);
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
INSERT INTO "assets" VALUES(1,1,1,'Primary Residence','joint',750000.0,0);
INSERT INTO "assets" VALUES(2,1,2,'401(k)','person1',500000.0,1);
INSERT INTO "assets" VALUES(3,1,2,'IRA','person2',350000.0,1);
INSERT INTO "assets" VALUES(4,1,3,'Stock Portfolio','joint',250000.0,1);
INSERT INTO "assets" VALUES(5,2,4,'Tech Portfolio','person1',300000.0,1);
INSERT INTO "assets" VALUES(6,2,5,'Bitcoin Holdings','person1',150000.0,1);
INSERT INTO "assets" VALUES(7,2,6,'Total Market ETF','person1',500000.0,1);
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
INSERT INTO "base_assumptions" VALUES(1,65,67,95,95,1,0.06,0.028);
INSERT INTO "base_assumptions" VALUES(2,45,NULL,90,NULL,1,0.07,0.03);
INSERT INTO "base_assumptions" VALUES(3,65,65,90,95,2,0.05,0.029);
INSERT INTO "base_assumptions" VALUES(4,62,65,92,92,1,0.055,0.026);
INSERT INTO "base_assumptions" VALUES(5,62,65,92,92,1,0.055,0.026);
INSERT INTO "base_assumptions" VALUES(6,58,60,95,95,1,0.065,0.031);
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
INSERT INTO "growth_rate_configurations" VALUES(1,2,NULL,NULL,'OVERRIDE',2024,NULL,0.07);
INSERT INTO "growth_rate_configurations" VALUES(2,3,NULL,NULL,'OVERRIDE',2024,NULL,0.065);
INSERT INTO "growth_rate_configurations" VALUES(3,4,NULL,NULL,'STEPWISE',2024,2026,0.08);
INSERT INTO "growth_rate_configurations" VALUES(4,4,NULL,NULL,'STEPWISE',2027,2030,0.06);
INSERT INTO "growth_rate_configurations" VALUES(5,5,NULL,NULL,'STEPWISE',2024,2025,0.15);
INSERT INTO "growth_rate_configurations" VALUES(6,5,NULL,NULL,'STEPWISE',2026,2027,0.1);
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
INSERT INTO "households" VALUES(1,'Test Household A','John','Smith','1970-05-15','Jane','Smith','1972-08-23','2025-01-28 05:52:00','2025-01-28 05:52:00');
INSERT INTO "households" VALUES(2,'Test Household B','Sarah','Johnson','1985-03-20',NULL,NULL,NULL,'2025-01-28 05:52:46','2025-01-28 05:52:46');
INSERT INTO "households" VALUES(3,'Test Household C','Robert','Miller','1960-08-10','Emma','Miller','1980-12-15','2025-01-28 05:58:02','2025-01-28 05:58:02');
INSERT INTO "households" VALUES(4,'Test Household D','Michael','Anderson','1965-11-22','Lisa','Anderson','1966-03-15','2025-01-28 06:13:37','2025-01-28 06:13:37');
INSERT INTO "households" VALUES(5,'Test Household E','David','Wilson','1975-04-30','Maria','Wilson','1978-09-12','2025-01-28 06:14:35','2025-01-28 06:14:35');
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
INSERT INTO "inflows_outflows" VALUES(1,1,'inflow','Salary Person 1','person1',120000.0,2024,2029,1);
INSERT INTO "inflows_outflows" VALUES(2,1,'inflow','Salary Person 2','person2',95000.0,2024,2031,1);
INSERT INTO "inflows_outflows" VALUES(3,1,'outflow','Property Tax','joint',8500.0,2024,NULL,1);
INSERT INTO "inflows_outflows" VALUES(4,2,'inflow','Tech Job Salary','person1',180000.0,2024,2030,1);
INSERT INTO "inflows_outflows" VALUES(5,2,'inflow','Rental Income','person1',36000.0,2024,NULL,1);
INSERT INTO "inflows_outflows" VALUES(6,2,'inflow','Side Consulting','person1',25000.0,2024,2026,0);
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
INSERT INTO "liabilities" VALUES(1,1,1,'Home Mortgage','joint',450000.0,0.0375,1);
INSERT INTO "liabilities" VALUES(2,1,2,'Car Loan','person1',35000.0,0.0425,1);
INSERT INTO "liabilities" VALUES(3,2,3,'Rental Property Mortgage','person1',300000.0,0.0425,1);
INSERT INTO "liabilities" VALUES(4,2,4,'Investment Line of Credit','person1',50000.0,0.065,1);
CREATE TABLE liability_categories (

    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    category_name TEXT NOT NULL,

    category_order INTEGER DEFAULT 0,               -- For UI ordering

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);
INSERT INTO "liability_categories" VALUES(1,1,'Mortgages',1);
INSERT INTO "liability_categories" VALUES(2,1,'Personal Loans',2);
INSERT INTO "liability_categories" VALUES(3,2,'Investment Property Loans',1);
INSERT INTO "liability_categories" VALUES(4,2,'Credit Lines',2);
INSERT INTO "liability_categories" VALUES(5,6,'International Mortgages',1);
INSERT INTO "liability_categories" VALUES(6,6,'Business Loans',2);
CREATE TABLE plans (

    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,

    household_id INTEGER NOT NULL,

    plan_name TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, reference_person INTEGER NOT NULL DEFAULT 1, plan_creation_year INTEGER,

    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE

);
INSERT INTO "plans" VALUES(1,1,'Base Retirement Plan','2025-01-28 05:52:00','2025-01-28 05:52:00',1,NULL);
INSERT INTO "plans" VALUES(2,2,'FIRE Strategy Plan','2025-01-28 05:52:46','2025-01-28 05:52:46',1,NULL);
INSERT INTO "plans" VALUES(3,2,'FIRE Strategy Plan','2025-01-28 05:53:31','2025-01-28 05:53:31',1,NULL);
INSERT INTO "plans" VALUES(4,3,'Staggered Retirement Plan','2025-01-28 05:58:02','2025-01-28 05:58:02',1,NULL);
INSERT INTO "plans" VALUES(5,4,'Pension Optimization Plan','2025-01-28 06:13:37','2025-01-28 06:13:37',1,NULL);
INSERT INTO "plans" VALUES(6,5,'International Retirement Plan','2025-01-28 06:14:35','2025-01-28 06:14:35',1,NULL);
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
INSERT INTO "retirement_income_plans" VALUES(1,1,'Social Security','person1',32000.0,67,NULL,1);
INSERT INTO "retirement_income_plans" VALUES(2,1,'Pension','person2',45000.0,65,NULL,1);
INSERT INTO "retirement_income_plans" VALUES(3,2,'Social Security','person1',28000.0,67,NULL,1);
INSERT INTO "retirement_income_plans" VALUES(4,2,'Rental Income Stream','person1',36000.0,45,NULL,1);
INSERT INTO "retirement_income_plans" VALUES(5,5,'Corporate Pension','person1',65000.0,62,NULL,1);
INSERT INTO "retirement_income_plans" VALUES(6,5,'State Pension','person2',42000.0,65,NULL,1);
CREATE TABLE scenario_assumptions (

    scenario_id INTEGER PRIMARY KEY,

    retirement_age_1 INTEGER,                       -- Age-based: Retirement planning is age-focused

    retirement_age_2 INTEGER,                       -- Age-based: Retirement planning is age-focused

    default_growth_rate REAL,                      -- Annual rate

    inflation_rate REAL,                           -- Annual rate

    annual_retirement_spending REAL,                -- Amount

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE

);
INSERT INTO "scenario_assumptions" VALUES(1,60,62,0.055,0.03,85000.0);
INSERT INTO "scenario_assumptions" VALUES(2,67,69,0.045,0.025,75000.0);
INSERT INTO "scenario_assumptions" VALUES(3,43,NULL,0.08,0.032,100000.0);
INSERT INTO "scenario_assumptions" VALUES(4,47,NULL,0.05,0.028,80000.0);
INSERT INTO "scenario_assumptions" VALUES(5,45,NULL,0.065,0.03,90000.0);
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
INSERT INTO "scenario_overrides" VALUES(1,1,2,NULL,NULL,NULL,'value','600000');
INSERT INTO "scenario_overrides" VALUES(2,2,4,NULL,NULL,NULL,'remove','TRUE');
INSERT INTO "scenario_overrides" VALUES(3,3,5,NULL,NULL,NULL,'value','400000');
INSERT INTO "scenario_overrides" VALUES(4,3,6,NULL,NULL,NULL,'remove','TRUE');
INSERT INTO "scenario_overrides" VALUES(5,4,5,NULL,NULL,NULL,'value','200000');
CREATE TABLE scenarios (

    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    scenario_name TEXT NOT NULL,

    scenario_color TEXT,                            -- For UI visualization

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);
INSERT INTO "scenarios" VALUES(1,1,'Early Retirement','#FF5733','2025-01-28 05:52:00');
INSERT INTO "scenarios" VALUES(2,1,'Conservative Growth','#33FF57','2025-01-28 05:52:00');
INSERT INTO "scenarios" VALUES(3,2,'Ultra Aggressive','#FF0000','2025-01-28 05:52:46');
INSERT INTO "scenarios" VALUES(4,2,'Market Correction','#0000FF','2025-01-28 05:52:46');
INSERT INTO "scenarios" VALUES(5,2,'Balanced Approach','#00FF00','2025-01-28 05:52:46');
INSERT INTO "scenarios" VALUES(6,5,'Early Pension Take','#4B0082','2025-01-28 06:13:37');
INSERT INTO "scenarios" VALUES(7,5,'Delayed Social Security','#800000','2025-01-28 06:13:37');
INSERT INTO "scenarios" VALUES(8,5,'Hybrid Approach','#006400','2025-01-28 06:13:37');
CREATE INDEX idx_households_name ON households (household_name);
CREATE INDEX idx_plans_household_id ON plans (household_id);
CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id);
CREATE INDEX idx_scenario_overrides_scenario_id ON scenario_overrides (scenario_id);
CREATE INDEX idx_scenario_overrides_asset_id ON scenario_overrides (asset_id);
CREATE INDEX idx_scenario_overrides_liability_id ON scenario_overrides (liability_id);
CREATE INDEX idx_scenario_overrides_inflow_outflow_id ON scenario_overrides (inflow_outflow_id);
CREATE INDEX idx_scenario_overrides_rip_id ON scenario_overrides (retirement_income_plan_id);
CREATE INDEX idx_asset_categories_plan_id ON asset_categories (plan_id);
CREATE INDEX idx_assets_plan_id ON assets (plan_id);
CREATE INDEX idx_assets_category_id ON assets (asset_category_id);
CREATE INDEX idx_liability_categories_plan_id ON liability_categories (plan_id);
CREATE INDEX idx_liabilities_plan_id ON liabilities (plan_id);
CREATE INDEX idx_liabilities_category_id ON liabilities (liability_category_id);
CREATE INDEX idx_inflows_outflows_plan_id ON inflows_outflows (plan_id);
CREATE INDEX idx_inflows_outflows_type ON inflows_outflows (type);
CREATE INDEX idx_inflows_outflows_years ON inflows_outflows (start_year, end_year);
CREATE INDEX idx_retirement_income_plans_plan_id ON retirement_income_plans (plan_id);
CREATE INDEX idx_growth_rate_configurations_asset_id ON growth_rate_configurations (asset_id);
CREATE INDEX idx_growth_rate_configurations_rip_id ON growth_rate_configurations (retirement_income_plan_id);
CREATE INDEX idx_growth_rate_configurations_scenario_id ON growth_rate_configurations (scenario_id);
CREATE INDEX idx_growth_rate_configurations_years ON growth_rate_configurations (start_year, end_year);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('households',5);
INSERT INTO "sqlite_sequence" VALUES('plans',6);
INSERT INTO "sqlite_sequence" VALUES('scenarios',8);
INSERT INTO "sqlite_sequence" VALUES('asset_categories',10);
INSERT INTO "sqlite_sequence" VALUES('inflows_outflows',6);
INSERT INTO "sqlite_sequence" VALUES('retirement_income_plans',6);
INSERT INTO "sqlite_sequence" VALUES('assets',7);
INSERT INTO "sqlite_sequence" VALUES('liability_categories',6);
INSERT INTO "sqlite_sequence" VALUES('liabilities',4);
INSERT INTO "sqlite_sequence" VALUES('growth_rate_configurations',6);
INSERT INTO "sqlite_sequence" VALUES('scenario_overrides',5);
COMMIT;
