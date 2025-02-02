# FIPLI_CORE_LOGIC.md

# This document contains specific details about the core data model and calculation logic of the FIPLI project.

################ FIPLI: Core Data Model & Calculation Logic ################

## Household
- Person 1: First/Last Name, DOB (required)
- Person 2: First/Last Name, DOB (optional)
- Ability to select which person’s DOB is used to determine the projection start year  
- Used for all year-based calculations  
- Manages multiple plans  

## Plans
- Each household → multiple plans  
- Each plan consists of:  
  1. Base Facts Aggregation  
  2. Scenarios  
  3. Projection  

**Base Facts Aggregation**  

## Asset Categories
- Customizable names (e.g., Qualified, Non-Qualified)  
- Assets can be assigned to categories  
- Categories for grouping/reporting only  

## Assets
- Value  
- Optional category assignment  
- Growth handling:  
  1. Default: Uses base assumption growth rate  
  2. Override: Asset-specific fixed rate  
  3. Stepwise: Multiple rates over time periods (start year / end year)  
  4. Gaps in stepwise fall to default  
- Optional inflation toggle  

## Liability Categories
- Customizable names (e.g., Personal, Business)  
- Liabilities can be assigned to categories  
- Categories for grouping/reporting only  

## Liabilities
- Value  
- Optional category assignment  
- Optional interest rate  
- Fixed value if no rate specified  
- No default growth rate usage, not affected by it  

## Scheduled Inflows/Outflows
- Start year, end year (stored as entered but converted as needed)  
- Amount  
- Optional inflation toggle  
- For discrete events only  
- Input in years  
- Examples: College (start year, end year different), inheritance (start year, end year the same)  

## Retirement Income
- Start year, end year  
- Amount  
- Optional inflation toggle  
- Input in absolute years (derived dynamically from selected person's retirement age)  
- For SS/Pension/Deferred Comp, etc.  
- Separate from scheduled inflows  

## Base Assumptions
- Default growth rate  
- Inflation rate  
- Retirement year (derived from selected retirement age)  
- End year (life expectancy year)  

** IMPORTANT: No retirement spending in base facts. Scenarios introduce a separate retirement spending parameter that does not modify existing scheduled outflows. **  

** NOTE: The start year is determined based on the selected household reference person's DOB. **  

## Scenarios
- Clone of base facts  
- Inherits all base facts and base assumptions  
- Can override any base fact as well as the fact’s parameters (like start and end year, or any other reasonable parameter) as well as base assumptions.  
- Unique: Has retirement spending  
- Retirement spending:  
  - Starts at retirement year  
  - Always inflation adjusted  
  - Common use: Max sustainable spend  
  - Can target zero at end year  

## Chart Projection
- Annual periods only  
- X-axis: Year-based (absolute years)  
- Y-axis: Portfolio value  
- Shows retirement nest egg  
- Not total net worth  
- Linear calculations only  
- No intra-year display  
- Dynamic updates on changes  

---
!!! THE ONLY VALIDATIONS ARE ONES THAT PREVENT IMPOSSIBILITIES NOT REASONABLENESS !!!



# Single Source of Truth

## Time Handling Principles
- DOB is the only true date input  
- All calculations reference absolute years internally  
- Conversion rules:  
  - DOB → Plan Creation Year: Determines the start year. Projections always begin in the year the plan was created, ensuring consistency across different plans and preventing shifting start points based on user age at different access times.
  - Years ↔ Age: Derived dynamically from DOB when needed  
  - Store values as entered by the user and convert as needed. aka “store what you know, convert in the backend”  

## Core Validations

(This app is designed for maximum flexibility. Validations ensure logical consistency without unnecessary restrictions, allowing accurate and user-driven projections.)  

1. Date of birth must be a valid past date.  
2. Retirement year must be after the start year.  
3. End year must be after retirement year.  
4. Start year must be before end year for inflows/outflows.  
5. Scenario overrides cannot create invalid timelines.  
6. Stepwise growth periods must be in chronological order and not overlap.  
7. Growth rate, inflation rate, and interest rate must be numeric and can be negative.  
8. Assets, liabilities, scheduled inflows, scheduled outflows, retirement income, and retirement spending must be positive values.  
9. Retirement spending cannot be negative.  

## Annual Calculation Order
1. Start with prior year-end values  
2. Apply scheduled inflows (inflation-adjusted if enabled)  
3. Apply scheduled outflows (inflation-adjusted if enabled)  
4. Apply retirement income  
5. Apply retirement spending  
6. Apply growth rates to remaining balance:  
   - Asset-specific rates first  
   - Default rates to remaining  
7. Apply liability interest  
8. Calculate year-end total  

## Value Display Principles
- All values shown in current dollars  
- Inflation adjustments compound annually  
- Growth compounds annually  
- No partial year or day counting  
- No cash flow timing within year  
- All events assumed to occur at year boundaries  
- Portfolio values represent year-end totals  

These rules deliberately simplified for:  
- Clear user understanding  
- Consistent calculations  
- Predictable results  
- Easy scenario comparison  
- Linear projection model integrity  

---

# KEY TAKEAWAYS  
- **Core modeling choice:** No intra-year calculations, strictly linear projections. Ensures predictability and transparency.  
- **Scenario overrides:** Each scenario is a sandbox that inherits base facts but can override parameters, allowing flexible "what-if" planning, including max sustainable spend calculations.  
- **Growth rate system:** Assets can have default, fixed, or stepwise growth rates, while liabilities use an optional interest rate instead of growth rates.  
- **Time handling:** The system uses absolute years as the primary reference for calculations, while the database stores the user’s original input and converts between formats as needed.  
- **Calculation flow:** A structured order ensures logical consistency, applying inflows, outflows, income, spending, growth, and liabilities sequentially.  
- **Validation rules:** Designed for flexibility while preventing illogical inputs, such as non-chronological stepwise growth periods or negative retirement spending.  
