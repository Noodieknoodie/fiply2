### Build Plan

#### Phase 1: Setup Core Structure
1. Create `database_operations/` folder with:
   - `models.py` (SQLAlchemy models for schema)
   - `connection.py` (database connection setup)
   - `financial_planner.db` (SQLite database file)

2. Write and test:
   - `test_connection.py` (verify database connection and basic table creation).

**File Hierarchy (Phase 1):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
└── tests/
    └── test_connection.py

---

#### Phase 2: Add Households
1. Define `households` table in `models.py`.
2. Create `crud/households.py` for CRUD operations.
3. Write and test:
   - `test_households.py` (test create, read, update, delete operations for households).

**File Hierarchy (Phase 2):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   └── households.py
└── tests/
    ├── test_connection.py
    └── test_households.py

---

#### Phase 3: Add Plans
1. Define `plans` table in `models.py`.
2. Add CRUD functions in `crud/plans.py`.
3. Write and test:
   - `test_plans.py` (test CRUD operations for plans, ensure linkage to households).

**File Hierarchy (Phase 3):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   ├── households.py
│   └── plans.py
└── tests/
    ├── test_connection.py
    ├── test_households.py
    └── test_plans.py

---

#### Phase 4: Add Base Assumptions
1. Define `base_assumptions` table in `models.py`.
2. Extend `crud/plans.py` for base assumptions handling.
3. Write and test:
   - `test_base_assumptions.py` (verify correct base assumption behavior per plan).

**File Hierarchy (Phase 4):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   ├── households.py
│   └── plans.py
└── tests/
    ├── test_connection.py
    ├── test_households.py
    ├── test_plans.py
    └── test_base_assumptions.py

---

#### Phase 5: Add Scenarios
1. Define `scenarios`, `scenario_assumptions`, and `scenario_overrides` in `models.py`.
2. Add CRUD functions in `crud/scenarios.py`.
3. Write and test:
   - `test_scenarios.py` (test scenario creation, overrides, and assumptions).

**File Hierarchy (Phase 5):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   ├── households.py
│   ├── plans.py
│   └── scenarios.py
└── tests/
    ├── test_connection.py
    ├── test_households.py
    ├── test_plans.py
    ├── test_base_assumptions.py
    └── test_scenarios.py

---

#### Phase 6: Add Financial Components
1. Define `assets`, `liabilities`, `inflows_outflows`, and `retirement_income_plans` in `models.py`.
2. Add CRUD functions in `crud/financial_components.py`.
3. Write and test:
   - `test_financial_components.py` (CRUD operations for assets, liabilities, inflows, and retirement income).

**File Hierarchy (Phase 6):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   ├── households.py
│   ├── plans.py
│   ├── scenarios.py
│   └── financial_components.py
└── tests/
    ├── test_connection.py
    ├── test_households.py
    ├── test_plans.py
    ├── test_base_assumptions.py
    ├── test_scenarios.py
    └── test_financial_components.py

---

#### Phase 7: Add Growth Rate Configurations
1. Define `growth_rate_configurations` in `models.py`.
2. Add CRUD functions in `crud/growth_rates.py`.
3. Write and test:
   - `test_growth_rates.py` (CRUD operations for growth rates, including default, custom, and stepwise).

**File Hierarchy (Phase 7):**
database_operations/
├── models.py
├── connection.py
├── financial_planner.db
├── crud/
│   ├── households.py
│   ├── plans.py
│   ├── scenarios.py
│   ├── financial_components.py
│   └── growth_rates.py
└── tests/
    ├── test_connection.py
    ├── test_households.py
    ├── test_plans.py
    ├── test_base_assumptions.py
    ├── test_scenarios.py
    ├── test_financial_components.py
    └── test_growth_rates.py
