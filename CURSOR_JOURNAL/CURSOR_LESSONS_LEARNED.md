backend\database_operations\database\fiply2_database.db 

# This file is for noting lessons learned from the project, focusing on non-obvious details, tricky concepts, and past issues to prevent future errors.



#MOTTO: "store what you know, calculate what you need." : Let the backend handle any necessary conversions between these formats based on the specific needs of the application. 

################ FIPLI: Lessons Learned #################

- Build core calculations first, ensuring functionality step by step  
- Create utility functions as needed for reusability and flexibility  
- Use relative imports (`from .connection import engine`) to avoid import errors  
- Drop/recreate tables in test cleanup to prevent stale data  
- Close sessions in `finally` blocks to prevent leaks  
- Never share sessions between tests to avoid data corruption  
- Use `lazy="joined"` only for small, frequently accessed relationships  
- Add `.unique()` when using joined loads to prevent duplicates  
- Refresh objects after adding relationships for visibility  
- Prefer `back_populates` over `backref` for explicit relationships  
- Store booleans as `INTEGER` (0/1) since SQLite lacks a boolean type  
- Use `check_same_thread=False` for multi-threaded tests  
- Use `StaticPool` for better test performance  
- Avoid unnecessary pagination  
- Don't create helper functions that duplicate SQLAlchemy features  
- Use `dataclasses` for simple data transfer objects instead of Pydantic  
- Use `autouse=True` for cleanup fixtures  
- Ensure each test has a complete environment  
- Never assume database state from previous tests  
- Clean up all data, not just what was created  
- Check record existence before update/delete operations  
- Use `try/finally` for session cleanup  
- Specify return types for clarity  
- Keep relationships simple, avoid excessive nesting  
- Reuse patterns across Assets, Liabilities, Cash Flows, and Retirement Income  
- Adapt to schema differences but avoid creating unnecessary patterns  
- Use `decimal.Decimal` for monetary values  
- Convert from `str()` to avoid float precision errors  
- Use `.quantize(Decimal('0.01'))` for currency consistency  
- Print actual vs expected values and relevant code  
- Verify fixes align with business logic, not just passing tests  
- Leverage existing utilities instead of duplicating logic  
- Create new functions only when necessary  
- Reset test data between runs  
- Ensure database sessions close properly  
- Use SQLite-specific handling (`check_same_thread=False`, `StaticPool`)  
