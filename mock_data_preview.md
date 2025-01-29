-- Table: sqlite_sequence --
CREATE TABLE sqlite_sequence (name, seq);

-- Table: households --
CREATE TABLE households (household_id, household_name, person1_first_name, person1_last_name, person1_dob, person2_first_name, person2_last_name, person2_dob, created_at, updated_at);
INSERT INTO households VALUES ('1', 'Test Household A', 'John', 'Smith', '1970-05-15', 'Jane', 'Smith', '1972-08-23', '2025-01-28 05:52:00', '2025-01-28 05:52:00');
INSERT INTO households VALUES ('2', 'Test Household B', 'Sarah', 'Johnson', '1985-03-20', NULL, NULL, NULL, '2025-01-28 05:52:46', '2025-01-28 05:52:46');
INSERT INTO households VALUES ('3', 'Test Household C', 'Robert', 'Miller', '1960-08-10', 'Emma', 'Miller', '1980-12-15', '2025-01-28 05:58:02', '2025-01-28 05:58:02');
INSERT INTO households VALUES ('4', 'Test Household D', 'Michael', 'Anderson', '1965-11-22', 'Lisa', 'Anderson', '1966-03-15', '2025-01-28 06:13:37', '2025-01-28 06:13:37');
INSERT INTO households VALUES ('5', 'Test Household E', 'David', 'Wilson', '1975-04-30', 'Maria', 'Wilson', '1978-09-12', '2025-01-28 06:14:35', '2025-01-28 06:14:35');

-- Table: plans --
CREATE TABLE plans (plan_id, household_id, plan_name, created_at, updated_at, description, is_active, target_fire_age, target_fire_amount, risk_tolerance);
INSERT INTO plans VALUES ('1', '1', 'Base Retirement Plan', '2025-01-28 05:52:00', '2025-01-28 05:52:00', 'Primary retirement strategy', '1', '55', '2000000.0', 'Moderate');
INSERT INTO plans VALUES ('2', '2', 'FIRE Strategy Plan', '2025-01-28 05:52:46', '2025-01-28 05:52:46', 'Aggressive early retirement plan', '1', '45', '3000000.0', 'Aggressive');
INSERT INTO plans VALUES ('3', '2', 'FIRE Strategy Plan', '2025-01-28 05:53:31', '2025-01-28 05:53:31', 'Aggressive early retirement plan', '1', '45', '3000000.0', 'Aggressive');
INSERT INTO plans VALUES ('4', '3', 'Staggered Retirement Plan', '2025-01-28 05:58:02', '2025-01-28 05:58:02', 'Plan for couple with 20-year age gap', '1', '65', '2500000.0', 'Conservative');
INSERT INTO plans VALUES ('5', '4', 'Pension Optimization Plan', '2025-01-28 06:13:37', '2025-01-28 06:13:37', 'Focus on pension and social security timing', '1', '60', '3500000.0', 'Moderate-Conservative');
INSERT INTO plans VALUES ('6', '5', 'International Retirement Plan', '2025-01-28 06:14:35', '2025-01-28 06:14:35', 'Multi-currency retirement strategy with overseas assets', '1', '58', '4000000.0', 'Aggressive');

-- Table: base_assumptions --
CREATE TABLE base_assumptions (plan_id, retirement_age_1, retirement_age_2, final_age_1, final_age_2, final_age_selector, default_growth_rate, inflation_rate);
INSERT INTO base_assumptions VALUES ('1', '65', '67', '95', '95', '1', '0.06', '0.028');
INSERT INTO base_assumptions VALUES ('2', '45', NULL, '90', NULL, '1', '0.07', '0.03');
INSERT INTO base_assumptions VALUES ('3', '65', '65', '90', '95', '2', '0.05', '0.029');
INSERT INTO base_assumptions VALUES ('4', '62', '65', '92', '92', '1', '0.055', '0.026');
INSERT INTO base_assumptions VALUES ('5', '62', '65', '92', '92', '1', '0.055', '0.026');
INSERT INTO base_assumptions VALUES ('6', '58', '60', '95', '95', '1', '0.065', '0.031');

-- Table: scenarios --
CREATE TABLE scenarios (scenario_id, plan_id, scenario_name, scenario_color, created_at);
INSERT INTO scenarios VALUES ('1', '1', 'Early Retirement', '#FF5733', '2025-01-28 05:52:00');
INSERT INTO scenarios VALUES ('2', '1', 'Conservative Growth', '#33FF57', '2025-01-28 05:52:00');
INSERT INTO scenarios VALUES ('3', '2', 'Ultra Aggressive', '#FF0000', '2025-01-28 05:52:46');
INSERT INTO scenarios VALUES ('4', '2', 'Market Correction', '#0000FF', '2025-01-28 05:52:46');
INSERT INTO scenarios VALUES ('5', '2', 'Balanced Approach', '#00FF00', '2025-01-28 05:52:46');
INSERT INTO scenarios VALUES ('6', '5', 'Early Pension Take', '#4B0082', '2025-01-28 06:13:37');
INSERT INTO scenarios VALUES ('7', '5', 'Delayed Social Security', '#800000', '2025-01-28 06:13:37');
INSERT INTO scenarios VALUES ('8', '5', 'Hybrid Approach', '#006400', '2025-01-28 06:13:37');
INSERT INTO scenarios VALUES ('9', '6', 'Crypto Boom', '#FFD700', '2025-01-28 06:14:35');
INSERT INTO scenarios VALUES ('10', '6', 'Startup Exit', '#9370DB', '2025-01-28 06:14:35');
INSERT INTO scenarios VALUES ('11', '6', 'Conservative Pivot', '#20B2AA', '2025-01-28 06:14:35');
INSERT INTO scenarios VALUES ('12', '6', 'Early Exit', '#FF6347', '2025-01-28 06:14:35');

-- Table: asset_categories --
CREATE TABLE asset_categories (asset_category_id, plan_id, category_name, category_order);
INSERT INTO asset_categories VALUES ('1', '1', 'Real Estate', '1');
INSERT INTO asset_categories VALUES ('2', '1', 'Retirement Accounts', '2');
INSERT INTO asset_categories VALUES ('3', '1', 'Investments', '3');
INSERT INTO asset_categories VALUES ('4', '2', 'Tech Stocks', '1');
INSERT INTO asset_categories VALUES ('5', '2', 'Crypto', '2');
INSERT INTO asset_categories VALUES ('6', '2', 'Index Funds', '3');
INSERT INTO asset_categories VALUES ('7', '2', 'Real Estate', '4');
INSERT INTO asset_categories VALUES ('8', '3', 'Business Assets', '1');
INSERT INTO asset_categories VALUES ('9', '3', 'Fixed Income', '2');
INSERT INTO asset_categories VALUES ('10', '3', 'International', '3');
INSERT INTO asset_categories VALUES ('11', '4', 'Pension Assets', '1');
INSERT INTO asset_categories VALUES ('12', '4', 'Taxable Accounts', '2');
INSERT INTO asset_categories VALUES ('13', '4', 'Alternative Investments', '3');
INSERT INTO asset_categories VALUES ('14', '5', 'Pension Assets', '1');
INSERT INTO asset_categories VALUES ('15', '5', 'Taxable Accounts', '2');
INSERT INTO asset_categories VALUES ('16', '5', 'Alternative Investments', '3');
INSERT INTO asset_categories VALUES ('17', '6', 'International Real Estate', '1');
INSERT INTO asset_categories VALUES ('18', '6', 'Global Equities', '2');
INSERT INTO asset_categories VALUES ('19', '6', 'Cryptocurrency', '3');
INSERT INTO asset_categories VALUES ('20', '6', 'Startup Investments', '4');

-- Table: liability_categories --
CREATE TABLE liability_categories (liability_category_id, plan_id, category_name, category_order);
INSERT INTO liability_categories VALUES ('1', '1', 'Mortgages', '1');
INSERT INTO liability_categories VALUES ('2', '1', 'Personal Loans', '2');
INSERT INTO liability_categories VALUES ('3', '2', 'Investment Property Loans', '1');
INSERT INTO liability_categories VALUES ('4', '2', 'Credit Lines', '2');
INSERT INTO liability_categories VALUES ('5', '4', 'Home Loans', '1');
INSERT INTO liability_categories VALUES ('6', '4', 'Investment Debt', '2');
INSERT INTO liability_categories VALUES ('7', '5', 'Home Loans', '1');
INSERT INTO liability_categories VALUES ('8', '5', 'Investment Debt', '2');
INSERT INTO liability_categories VALUES ('9', '6', 'International Mortgages', '1');
INSERT INTO liability_categories VALUES ('10', '6', 'Business Loans', '2');
INSERT INTO liability_categories VALUES ('11', '6', 'Personal Credit', '3');

-- Table: inflows_outflows --
CREATE TABLE inflows_outflows (inflow_outflow_id, plan_id, type, name, annual_amount, start_date, end_date, apply_inflation);
INSERT INTO inflows_outflows VALUES ('1', '1', 'INFLOW', 'Salary Person 1', '120000.0', '2024-01-01', '2029-12-31', '1');
INSERT INTO inflows_outflows VALUES ('2', '1', 'INFLOW', 'Salary Person 2', '95000.0', '2024-01-01', '2031-12-31', '1');
INSERT INTO inflows_outflows VALUES ('3', '1', 'OUTFLOW', 'Property Tax', '8500.0', '2024-01-01', NULL, '1');
INSERT INTO inflows_outflows VALUES ('4', '2', 'INFLOW', 'Tech Job Salary', '180000.0', '2024-01-01', '2030-12-31', '1');
INSERT INTO inflows_outflows VALUES ('5', '2', 'INFLOW', 'Rental Income', '36000.0', '2024-01-01', NULL, '1');
INSERT INTO inflows_outflows VALUES ('6', '2', 'INFLOW', 'Side Consulting', '25000.0', '2024-01-01', '2026-12-31', '0');
INSERT INTO inflows_outflows VALUES ('7', '2', 'OUTFLOW', 'Property Management', '3600.0', '2024-01-01', NULL, '1');
INSERT INTO inflows_outflows VALUES ('8', '5', 'INFLOW', 'Person 1 Salary', '160000.0', '2024-01-01', '2029-12-31', '1');
INSERT INTO inflows_outflows VALUES ('9', '5', 'INFLOW', 'Person 2 Consulting', '85000.0', '2024-01-01', '2031-12-31', '1');
INSERT INTO inflows_outflows VALUES ('10', '5', 'OUTFLOW', 'Healthcare Premiums', '15000.0', '2024-01-01', NULL, '1');
INSERT INTO inflows_outflows VALUES ('11', '6', 'INFLOW', 'Tech Executive Salary', '225000.0', '2024-01-01', '2028-12-31', '1');
INSERT INTO inflows_outflows VALUES ('12', '6', 'INFLOW', 'Rental Income London', '45000.0', '2024-01-01', NULL, '1');
INSERT INTO inflows_outflows VALUES ('13', '6', 'INFLOW', 'Consulting Revenue', '80000.0', '2024-01-01', '2030-12-31', '1');
INSERT INTO inflows_outflows VALUES ('14', '6', 'OUTFLOW', 'International Property Management', '12000.0', '2024-01-01', NULL, '1');

-- Table: scenario_assumptions --
CREATE TABLE scenario_assumptions (scenario_id, retirement_age_1, retirement_age_2, default_growth_rate, inflation_rate, annual_retirement_spending);
INSERT INTO scenario_assumptions VALUES ('1', '60', '62', '0.055', '0.03', '85000.0');
INSERT INTO scenario_assumptions VALUES ('2', '67', '69', '0.045', '0.025', '75000.0');
INSERT INTO scenario_assumptions VALUES ('3', '43', NULL, '0.08', '0.032', '100000.0');
INSERT INTO scenario_assumptions VALUES ('4', '47', NULL, '0.05', '0.028', '80000.0');
INSERT INTO scenario_assumptions VALUES ('5', '45', NULL, '0.065', '0.03', '90000.0');
INSERT INTO scenario_assumptions VALUES ('6', '60', '62', '0.052', '0.027', '110000.0');
INSERT INTO scenario_assumptions VALUES ('7', '65', '67', '0.057', '0.025', '95000.0');
INSERT INTO scenario_assumptions VALUES ('8', '62', '65', '0.054', '0.026', '102000.0');
INSERT INTO scenario_assumptions VALUES ('9', '55', '57', '0.072', '0.035', '150000.0');
INSERT INTO scenario_assumptions VALUES ('10', '53', '55', '0.068', '0.033', '180000.0');
INSERT INTO scenario_assumptions VALUES ('11', '62', '64', '0.045', '0.028', '120000.0');
INSERT INTO scenario_assumptions VALUES ('12', '50', '52', '0.075', '0.034', '200000.0');

-- Table: assets --
CREATE TABLE assets (asset_id, plan_id, asset_category_id, asset_name, owner, value, include_in_nest_egg);
INSERT INTO assets VALUES ('1', '1', '1', 'Primary Residence', 'Joint', '750000.0', '0');
INSERT INTO assets VALUES ('2', '1', '2', '401(k)', 'Person 1', '500000.0', '1');
INSERT INTO assets VALUES ('3', '1', '2', 'IRA', 'Person 2', '350000.0', '1');
INSERT INTO assets VALUES ('4', '1', '3', 'Stock Portfolio', 'Joint', '250000.0', '1');
INSERT INTO assets VALUES ('5', '2', '1', 'Tech Portfolio', 'Person 1', '300000.0', '1');
INSERT INTO assets VALUES ('6', '2', '2', 'Bitcoin Holdings', 'Person 1', '150000.0', '1');
INSERT INTO assets VALUES ('7', '2', '3', 'Total Market ETF', 'Person 1', '500000.0', '1');
INSERT INTO assets VALUES ('8', '2', '4', 'Rental Property', 'Person 1', '400000.0', '1');
INSERT INTO assets VALUES ('9', '4', '10', 'Pension Lump Sum Option', 'Person 1', '800000.0', '1');
INSERT INTO assets VALUES ('10', '4', '11', 'Brokerage Account', 'Joint', '650000.0', '1');
INSERT INTO assets VALUES ('11', '4', '12', 'Private Equity Fund', 'Person 2', '200000.0', '0');
INSERT INTO assets VALUES ('12', '5', '14', 'Pension Lump Sum Option', 'Person 1', '800000.0', '1');
INSERT INTO assets VALUES ('13', '5', '15', 'Brokerage Account', 'Joint', '650000.0', '1');
INSERT INTO assets VALUES ('14', '5', '16', 'Private Equity Fund', 'Person 2', '200000.0', '0');
INSERT INTO assets VALUES ('15', '6', '17', 'London Property', 'Joint', '900000.0', '1');
INSERT INTO assets VALUES ('16', '6', '18', 'Global ETF Portfolio', 'Person 1', '750000.0', '1');
INSERT INTO assets VALUES ('17', '6', '19', 'Bitcoin Holdings', 'Person 2', '100000.0', '0');
INSERT INTO assets VALUES ('18', '6', '20', 'Tech Startup Shares', 'Person 1', '250000.0', '0');

-- Table: liabilities --
CREATE TABLE liabilities (liability_id, plan_id, liability_category_id, liability_name, owner, value, interest_rate, include_in_nest_egg);
INSERT INTO liabilities VALUES ('1', '1', '1', 'Home Mortgage', 'Joint', '450000.0', '0.0375', '1');
INSERT INTO liabilities VALUES ('2', '1', '2', 'Car Loan', 'Person 1', '35000.0', '0.0425', '1');
INSERT INTO liabilities VALUES ('3', '2', '3', 'Rental Property Mortgage', 'Person 1', '300000.0', '0.0425', '1');
INSERT INTO liabilities VALUES ('4', '2', '4', 'Investment Line of Credit', 'Person 1', '50000.0', '0.065', '1');
INSERT INTO liabilities VALUES ('5', '5', '7', 'HELOC', 'Joint', '150000.0', '0.0575', '1');
INSERT INTO liabilities VALUES ('6', '5', '8', 'Investment Property Loan', 'Person 2', '300000.0', '0.0425', '0');
INSERT INTO liabilities VALUES ('7', '6', '9', 'London Mortgage', 'Joint', '600000.0', '0.0325', '1');
INSERT INTO liabilities VALUES ('8', '6', '10', 'Startup Loan', 'Person 1', '150000.0', '0.0675', '1');
INSERT INTO liabilities VALUES ('9', '6', '11', 'Credit Lines', 'Person 2', '25000.0', '0.089', '0');

-- Table: scenario_overrides --
CREATE TABLE scenario_overrides (override_id, scenario_id, asset_id, liability_id, inflow_outflow_id, retirement_income_plan_id, override_field, override_value);
INSERT INTO scenario_overrides VALUES ('1', '1', '2', NULL, NULL, NULL, 'value', '600000');
INSERT INTO scenario_overrides VALUES ('2', '2', '4', NULL, NULL, NULL, 'remove', 'TRUE');
INSERT INTO scenario_overrides VALUES ('3', '3', '5', NULL, NULL, NULL, 'value', '400000');
INSERT INTO scenario_overrides VALUES ('4', '3', '6', NULL, NULL, NULL, 'remove', 'TRUE');
INSERT INTO scenario_overrides VALUES ('5', '4', '5', NULL, NULL, NULL, 'value', '200000');
INSERT INTO scenario_overrides VALUES ('6', '4', '7', NULL, NULL, NULL, 'value', '400000');
INSERT INTO scenario_overrides VALUES ('7', '5', '8', NULL, NULL, NULL, 'include_in_nest_egg', 'FALSE');
INSERT INTO scenario_overrides VALUES ('8', '3', NULL, NULL, '5', NULL, 'annual_amount', '200000');
INSERT INTO scenario_overrides VALUES ('9', '4', NULL, NULL, '6', NULL, 'end_date', '2025-12-31');
INSERT INTO scenario_overrides VALUES ('10', '6', NULL, NULL, NULL, '5', 'annual_income', '55000');
INSERT INTO scenario_overrides VALUES ('11', '6', NULL, NULL, NULL, '6', 'start_age', '60');
INSERT INTO scenario_overrides VALUES ('12', '7', NULL, NULL, NULL, '7', 'annual_income', '42000');
INSERT INTO scenario_overrides VALUES ('13', '8', NULL, NULL, NULL, '8', 'end_age', '90');
INSERT INTO scenario_overrides VALUES ('14', '9', '17', NULL, NULL, NULL, 'value', '500000');
INSERT INTO scenario_overrides VALUES ('15', '10', '18', NULL, NULL, NULL, 'value', '2000000');
INSERT INTO scenario_overrides VALUES ('16', '11', '17', NULL, NULL, NULL, 'remove', 'TRUE');
INSERT INTO scenario_overrides VALUES ('17', '12', '18', NULL, NULL, NULL, 'value', '3000000');
INSERT INTO scenario_overrides VALUES ('18', '9', NULL, NULL, NULL, '9', 'annual_income', '50000');
INSERT INTO scenario_overrides VALUES ('19', '10', NULL, NULL, NULL, '10', 'start_age', '55');
INSERT INTO scenario_overrides VALUES ('20', '11', NULL, NULL, NULL, '11', 'end_age', '75');
INSERT INTO scenario_overrides VALUES ('21', '12', NULL, NULL, NULL, '11', 'annual_income', '100000');

-- Table: growth_rate_configurations --
CREATE TABLE growth_rate_configurations (growth_rate_id, asset_id, retirement_income_plan_id, scenario_id, configuration_type, start_date, end_date, growth_rate);
INSERT INTO growth_rate_configurations VALUES ('1', '2', NULL, NULL, 'OVERRIDE', NULL, NULL, '0.07');
INSERT INTO growth_rate_configurations VALUES ('2', '3', NULL, NULL, 'OVERRIDE', NULL, NULL, '0.065');
INSERT INTO growth_rate_configurations VALUES ('3', '4', NULL, NULL, 'STEPWISE', '2024-01-01', '2026-12-31', '0.08');
INSERT INTO growth_rate_configurations VALUES ('4', '4', NULL, NULL, 'STEPWISE', '2027-01-01', '2030-12-31', '0.06');
INSERT INTO growth_rate_configurations VALUES ('5', '5', NULL, NULL, 'STEPWISE', '2024-01-01', '2025-12-31', '0.15');
INSERT INTO growth_rate_configurations VALUES ('6', '5', NULL, NULL, 'STEPWISE', '2026-01-01', '2027-12-31', '0.1');
INSERT INTO growth_rate_configurations VALUES ('7', '5', NULL, NULL, 'STEPWISE', '2028-01-01', '2030-12-31', '0.06');
INSERT INTO growth_rate_configurations VALUES ('8', '6', NULL, NULL, 'STEPWISE', '2024-01-01', '2024-12-31', '0.25');
INSERT INTO growth_rate_configurations VALUES ('9', '6', NULL, NULL, 'STEPWISE', '2025-01-01', '2026-12-31', '0.12');
INSERT INTO growth_rate_configurations VALUES ('10', '6', NULL, NULL, 'STEPWISE', '2027-01-01', NULL, '0.08');
INSERT INTO growth_rate_configurations VALUES ('11', '12', NULL, NULL, 'STEPWISE', '2024-01-01', '2026-12-31', '0.07');
INSERT INTO growth_rate_configurations VALUES ('12', '12', NULL, NULL, 'STEPWISE', '2027-01-01', '2029-12-31', '0.045');
INSERT INTO growth_rate_configurations VALUES ('13', '13', NULL, NULL, 'OVERRIDE', NULL, NULL, '0.062');
INSERT INTO growth_rate_configurations VALUES ('14', '15', NULL, NULL, 'STEPWISE', '2024-01-01', '2025-12-31', '0.04');
INSERT INTO growth_rate_configurations VALUES ('15', '15', NULL, NULL, 'STEPWISE', '2026-01-01', '2028-12-31', '0.06');
INSERT INTO growth_rate_configurations VALUES ('16', '16', NULL, NULL, 'OVERRIDE', NULL, NULL, '0.085');
INSERT INTO growth_rate_configurations VALUES ('17', '17', NULL, NULL, 'STEPWISE', '2024-01-01', '2024-12-31', '0.5');
INSERT INTO growth_rate_configurations VALUES ('18', '17', NULL, NULL, 'STEPWISE', '2025-01-01', '2026-12-31', '0.2');
INSERT INTO growth_rate_configurations VALUES ('19', '18', NULL, NULL, 'STEPWISE', '2024-01-01', '2026-12-31', '0.15');

-- Table: retirement_income_plans --
CREATE TABLE retirement_income_plans (income_plan_id, plan_id, name, owner, annual_income, start_age, end_age, include_in_nest_egg, apply_inflation);
INSERT INTO retirement_income_plans VALUES ('1', '1', 'Social Security', 'Person 1', '32000.0', '67', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('2', '1', 'Pension', 'Person 2', '45000.0', '65', NULL, '1', '0');
INSERT INTO retirement_income_plans VALUES ('3', '2', 'Social Security', 'Person 1', '28000.0', '67', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('4', '2', 'Rental Income Stream', 'Person 1', '36000.0', '45', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('5', '5', 'Corporate Pension', 'Person 1', '65000.0', '62', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('6', '5', 'State Pension', 'Person 2', '42000.0', '65', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('7', '5', 'Social Security', 'Person 1', '34000.0', '67', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('8', '5', 'Social Security', 'Person 2', '28000.0', '67', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('9', '6', 'UK Pension', 'Person 1', '40000.0', '58', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('10', '6', 'EU Pension', 'Person 2', '35000.0', '60', NULL, '1', '1');
INSERT INTO retirement_income_plans VALUES ('11', '6', 'Deferred Comp Plan', 'Person 1', '75000.0', '58', '68', '1', '0');

