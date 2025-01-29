# FIPLI Refactoring Log  

## Phase 1: Utility Layer Refactoring ✅  

### Goal  
Shift to year-based calculations, ditch date complexity, and streamline projections.  

### Changes  

#### `date_utils.py` ✅  
— **Kept:** `calculate_current_age()` (DOB → Age)  
— **Added:**  
   — `calculate_age_for_year(dob, year) → int` (projection-friendly)  
   — `get_current_year() → int` (baseline helper)  
   — `generate_projection_years(start, end) → List[int]` (sequential years)  
   — `is_retirement_age(current, retirement) → bool` (simple check)  
   — `get_final_year(dob, final_age) → int` (projection endpoint)  
— **Removed:** Date-based calculations, prorated amounts, complex logic  

#### `money_utils.py` ✅  
— **Added:**  
   — `apply_annual_growth(amount, rate) → Decimal`  
   — `apply_annual_inflation(amount, rate) → Decimal`  

### Tests ✅  
— `test_date_utils.py`: Year-based focus, removed date arithmetic  
— `test_money_utils.py`: Growth functions, decimal precision  

### Breaking Changes 🚨  
— No date-based calculations, all year-based  
— No prorated or month-based values  
— All events occur at the start of the year  

### Next Steps  
1. [ ] Full test suite run  
2. [ ] Migration guide for dependent code  
3. [ ] Update documentation  
4. [ ] Plan **Phase 2: Core Calculations Refactor**  

---

## Phase 2: Core Calculation Refactoring ⏳  

### Goal  
Convert all projections to year-based logic, ensuring consistency across financial models.  

### Modules & Priorities  
#### **1. Base Value Calculators**  
— Implement **year-based** value tracking  
— Follow event sequence: **Inflows → Inflation → Spending → Growth**  

#### **2. Retirement Income**  
— Switch to **age-based** activation  
— Integrate **inflation + nest egg tracking**  

#### **3. Cash Flow**  
— Convert to **year-based timing**  
— Track **start/end year logic + nest egg impacts**  

#### **4. Assets/Liabilities**  
— Apply **year-based growth**  
— Handle **scenario overrides + rate configs**  

#### **5. Aggregator**  
— Implement **year-based aggregation**  
— Sequence events, track **nest egg trajectory**  

### Testing Strategy  
— Independent module tests ✅  
— Integration tests ✅  
— Edge cases + scenario handling ✅  

### Status: Planning ⏳  
— [ ] Review current models  
— [ ] Create test cases  
— [ ] Begin refactor  
— [ ] Update documentation  

---
