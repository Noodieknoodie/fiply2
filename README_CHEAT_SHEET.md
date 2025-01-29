# CHEAT SHEET 

# Base Facts Cheat Sheet

---

## Assets

### Adding an asset with default growth rate:

asset_id = 1  
asset_name = 'Real Estate'  
value = 500000  
growth_rate = NULL  -- Uses default growth rate  
include_in_nest_egg = TRUE  

### Adding an asset with custom growth rate:

growth_rate = 0.06  -- Custom growth rate (6%)  

### Adding an asset with stepwise growth rates:

growth_rate = NULL  -- Stepwise handled in growth_rate_configurations  

### Excluding an asset from the nest egg:

include_in_nest_egg = FALSE  

### Adding an asset with ownership details:

owner = 'Person 1'  -- Indicates ownership by Person 1  

---

## Liabilities

### Adding a liability with default interest rate:

liability_id = 1  
liability_name = 'Mortgage'  
value = 300000  
interest_rate = NULL  -- Uses default growth rate  
include_in_nest_egg = TRUE  

### Adding a liability with custom interest rate:

interest_rate = 0.035  -- Custom interest rate (3.5%)  

### Excluding a liability from the nest egg:

include_in_nest_egg = FALSE  

### Adding a liability with ownership details:

owner = 'Joint'  -- Indicates shared ownership  

---

## Inflows and Outflows

### Adding a recurring cash inflow with inflation:

inflow_outflow_id = 1  
type = 'INFLOW'  
name = 'Rental Income'  
annual_amount = 24000  
start_date = '2025-01-01'  
end_date = '2035-12-31'  
apply_inflation = TRUE  

### Adding a one-time cash inflow:

type = 'INFLOW'  
name = 'Bonus Payment'  
annual_amount = 10000  
start_date = '2024-06-01'  
end_date = '2024-06-01'  -- Same date for one-time payment  

### Adding a recurring cash outflow:

type = 'OUTFLOW'  
name = 'Car Lease'  
annual_amount = 6000  
start_date = '2024-01-01'  
end_date = '2028-12-31'  
apply_inflation = FALSE  

---

## Retirement Income Plans

### Adding a retirement income plan with default growth rate:

income_plan_id = 1  
name = 'Social Security'  
owner = 'Person 1'  
annual_income = 18000  
start_age = 67  
end_age = NULL  -- Lifetime income  
include_in_nest_egg = TRUE  

### Adding a retirement income plan with custom growth rate:

growth_rate = 0.02  -- Custom growth rate (2%)  

---

## Global Assumptions

### Setting default growth rate:

default_growth_rate = 0.05  -- Default growth rate of 5%  

### Setting inflation rate:

inflation_rate = 0.03  -- Global inflation rate of 3%  

### Setting retirement ages:

retirement_age_1 = 65  -- Retirement age for Person 1  
retirement_age_2 = 67  -- Retirement age for Person 2  

### Setting final planning ages:

final_age_1 = 95  -- Final age for Person 1  
final_age_2 = 90  -- Final age for Person 2  
final_age_selector = 1  -- Use Person 1's final age for calculations  

---

# Scenario Overrides Cheat Sheet

---

## What Are Scenario Overrides?  
Scenario overrides allow advisors to modify specific parameters of base facts for a given scenario without affecting the original data. These overrides are stored in the `scenario_overrides` table and can include actions such as changing values, adding stepwise growth rates, or removing entries.

---

## Examples of Scenario Overrides

### Removing an Asset from a Scenario:

asset_id = 1  
override_field = 'remove'  
override_value = TRUE  
scenario_id = 2  -- Scenario-specific removal  

### Adding a Custom Growth Rate to an Asset:

asset_id = 2  
override_field = 'growth_rate'  
override_value = 0.06  -- Custom growth rate (6%)  
scenario_id = 3  

### Adding Stepwise Growth Rates to an Asset:

Each time period for a stepwise growth rate is stored as a separate entry.

-- First period: 3% growth from 2025-01-01 to 2030-12-31  
asset_id = 3  
override_field = 'growth_rate'  
override_value = NULL  -- Stepwise entries handled in growth_rate_configurations  
scenario_id = 3  

start_date = '2025-01-01'  
end_date = '2030-12-31'  
growth_rate = 0.03  

-- Second period: 5% growth from 2031-01-01 to 2040-12-31  
start_date = '2031-01-01'  
end_date = '2040-12-31'  
growth_rate = 0.05  

### Changing the Value of an Asset:

asset_id = 1  
override_field = 'value'  
override_value = 600000  -- New value for the asset  
scenario_id = 2  

### Changing the Start Date of a Cash Inflow:

inflow_outflow_id = 4  
override_field = 'start_date'  
override_value = '2026-01-01'  -- New start date  
scenario_id = 3  

### Adjusting Annual Amount for a Cash Outflow:

inflow_outflow_id = 5  
override_field = 'annual_amount'  
override_value = 15000  -- Updated annual outflow amount  
scenario_id = 3  

### Excluding a Liability from a Scenario:

liability_id = 6  
override_field = 'remove'  
override_value = TRUE  -- Excludes liability from scenario  
scenario_id = 3  

### Modifying Default Growth Rate for the Scenario:

override_field = 'default_growth_rate'  
override_value = 0.04  -- Updated default growth rate (4%)  
scenario_id = 2  

### Setting Scenario-Specific Nest Egg Inclusion:

asset_id = 2  
override_field = 'include_in_nest_egg'  
override_value = FALSE  -- Excludes asset from nest egg calculations  
scenario_id = 3  

### Changing Retirement Ages for the Scenario:

override_field = 'retirement_age_1'  
override_value = 62  -- Updated retirement age for Person 1  
scenario_id = 4  

override_field = 'retirement_age_2'  
override_value = 65  -- Updated retirement age for Person 2  

### Adjusting Annual Retirement Spending:

override_field = 'annual_retirement_spending'  
override_value = 70000  -- Updated spending amount for this scenario  
scenario_id = 4  

---

Notes:  
- **Entity Type and IDs**: Columns like `asset_id`, `liability_id`, and `inflow_outflow_id` ensure explicit referencing of components in the schema.  
- **Override Field**: Indicates which field is being modified (e.g., ‘value’, ‘growth_rate’).  
- **Override Value**: Stores the updated value for that field.  
