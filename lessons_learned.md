#MOTTO: "store what you know, calculate what you need." : Let the backend handle any necessary conversions between these formats based on the specific needs of the application. 


Development Flow
The flow starts by building out the core calculations to handle all the necessary data, step by step, ensuring the basics work first. As the need arises, utility functions are created to handle repetitive or complex tasks, keeping the system clean, reusable, and flexible for future features.
Critical Lessons from Actual Errors

Database/Session Issues:

ALWAYS use relative imports (e.g., from .connection import engine) - caused import errors
ALWAYS drop and recreate tables in test cleanup - tests failed due to stale data
ALWAYS close sessions in finally blocks - caused session leaks
NEVER share sessions between tests - caused mysterious data issues


SQLAlchemy Relationship Issues:

Use lazy="joined" ONLY for small, frequently accessed relationships
Add .unique() when using joined loads to prevent duplicate rows
Refresh objects after adding relationships to see them
Use back_populates instead of backref for explicit relationships


SQLite Specific Issues:

Store booleans as INTEGER (0/1) - SQLite doesn't have true boolean type
Use check_same_thread=False for SQLite in tests
Use StaticPool for better test performance


Common Code Mistakes:

Don't over-engineer with pagination unless specifically needed
Don't add "helper" functions that duplicate SQLAlchemy features
Don't use Pydantic unless building an API
Use dataclasses for simple data transfer objects


Test Fixtures:

Use autouse=True for cleanup fixtures
Create complete test environment in each test
Don't assume database state from previous tests
Clean up ALL data, not just the data you created


Error Prevention:

Check if record exists before update/delete operations
Use try/finally for session cleanup
Always specify return types for clarity
Keep relationships simple - don't over-nest



CALCULATIONS LESSONS LEARNED

Pattern Reuse Across Calculations

Mirror existing calculation structures (Assets, Liabilities, Cash Flows, Retirement Income)
Adapt to schema differences but avoid unnecessary new patterns


Precision & Financial Calculations

Use decimal.Decimal for all monetary values
Convert from str() to avoid float precision errors
Use .quantize(Decimal('0.01')) for currency consistency


Debugging Test Failures

Print actual vs expected values, relevant code, and check README/schema
Ensure fixes follow business logic, not just pass tests


Code Reuse & Helpers

Use existing utilities instead of duplicating logic
Only create new functions when necessary


Test Environment Consistency

Always reset test data between runs
Ensure database sessions close properly
Use SQLite-specific handling (check_same_thread=False, StaticPool)


SQLAlchemy Best Practices

Use back_populates instead of backref
Optimize queries—use lazy="joined" only when needed
Keep relationships simple and explicit