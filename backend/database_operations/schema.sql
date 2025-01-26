-- Generated schema from SQLAlchemy models


CREATE TABLE asset_categories (
	asset_category_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	category_name VARCHAR NOT NULL, 
	category_order INTEGER NOT NULL, 
	PRIMARY KEY (asset_category_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;


CREATE TABLE assets (
	asset_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	asset_category_id INTEGER NOT NULL, 
	asset_name VARCHAR NOT NULL, 
	owner VARCHAR NOT NULL, 
	value FLOAT NOT NULL, 
	include_in_nest_egg INTEGER NOT NULL, 
	PRIMARY KEY (asset_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE, 
	FOREIGN KEY(asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
)

;


CREATE TABLE base_assumptions (
	plan_id INTEGER NOT NULL, 
	retirement_age_1 INTEGER, 
	retirement_age_2 INTEGER, 
	final_age_1 INTEGER, 
	final_age_2 INTEGER, 
	final_age_selector INTEGER, 
	default_growth_rate FLOAT, 
	inflation_rate FLOAT, 
	PRIMARY KEY (plan_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;


CREATE TABLE growth_rate_configurations (
	growth_rate_id INTEGER NOT NULL, 
	asset_id INTEGER, 
	retirement_income_plan_id INTEGER, 
	scenario_id INTEGER, 
	configuration_type VARCHAR NOT NULL, 
	start_date DATE, 
	end_date DATE, 
	growth_rate FLOAT NOT NULL, 
	PRIMARY KEY (growth_rate_id), 
	FOREIGN KEY(asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE, 
	FOREIGN KEY(retirement_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE, 
	FOREIGN KEY(scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
)

;


CREATE TABLE households (
	household_id INTEGER NOT NULL, 
	household_name VARCHAR NOT NULL, 
	person1_first_name VARCHAR NOT NULL, 
	person1_last_name VARCHAR NOT NULL, 
	person1_dob DATE NOT NULL, 
	person2_first_name VARCHAR, 
	person2_last_name VARCHAR, 
	person2_dob DATE, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (household_id)
)

;


CREATE TABLE inflows_outflows (
	inflow_outflow_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	type VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	annual_amount FLOAT NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE, 
	apply_inflation INTEGER NOT NULL, 
	PRIMARY KEY (inflow_outflow_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;


CREATE TABLE liabilities (
	liability_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	liability_category_id INTEGER NOT NULL, 
	liability_name VARCHAR NOT NULL, 
	owner VARCHAR NOT NULL, 
	value FLOAT NOT NULL, 
	interest_rate FLOAT, 
	include_in_nest_egg INTEGER NOT NULL, 
	PRIMARY KEY (liability_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE, 
	FOREIGN KEY(liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
)

;


CREATE TABLE liability_categories (
	liability_category_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	category_name VARCHAR NOT NULL, 
	category_order INTEGER NOT NULL, 
	PRIMARY KEY (liability_category_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;


CREATE TABLE plans (
	plan_id INTEGER NOT NULL, 
	household_id INTEGER NOT NULL, 
	plan_name VARCHAR(100) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	description VARCHAR(500), 
	is_active BOOLEAN NOT NULL, 
	target_fire_age INTEGER, 
	target_fire_amount FLOAT, 
	risk_tolerance VARCHAR(50), 
	PRIMARY KEY (plan_id), 
	FOREIGN KEY(household_id) REFERENCES households (household_id) ON DELETE CASCADE
)

;


CREATE TABLE retirement_income_plans (
	income_plan_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	owner VARCHAR NOT NULL, 
	annual_income FLOAT NOT NULL, 
	start_age INTEGER NOT NULL, 
	end_age INTEGER, 
	include_in_nest_egg INTEGER NOT NULL,
	apply_inflation INTEGER DEFAULT 0 NOT NULL,
	PRIMARY KEY (income_plan_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;


CREATE TABLE scenario_assumptions (
	scenario_id INTEGER NOT NULL, 
	retirement_age_1 INTEGER, 
	retirement_age_2 INTEGER, 
	default_growth_rate FLOAT, 
	inflation_rate FLOAT, 
	annual_retirement_spending FLOAT, 
	PRIMARY KEY (scenario_id), 
	FOREIGN KEY(scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
)

;


CREATE TABLE scenario_overrides (
	override_id INTEGER NOT NULL, 
	scenario_id INTEGER NOT NULL, 
	asset_id INTEGER, 
	liability_id INTEGER, 
	inflow_outflow_id INTEGER, 
	retirement_income_plan_id INTEGER, 
	override_field VARCHAR NOT NULL, 
	override_value VARCHAR NOT NULL, 
	PRIMARY KEY (override_id), 
	FOREIGN KEY(scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE, 
	FOREIGN KEY(asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE, 
	FOREIGN KEY(liability_id) REFERENCES liabilities (liability_id) ON DELETE CASCADE, 
	FOREIGN KEY(inflow_outflow_id) REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE, 
	FOREIGN KEY(retirement_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE
)

;


CREATE TABLE scenarios (
	scenario_id INTEGER NOT NULL, 
	plan_id INTEGER NOT NULL, 
	scenario_name VARCHAR NOT NULL, 
	scenario_color VARCHAR, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (scenario_id), 
	FOREIGN KEY(plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)

;

