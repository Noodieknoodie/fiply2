# Critical Lessons from Actual Errors

1. Database/Session Issues:
   - ALWAYS use relative imports (e.g., from .connection import engine) - caused import errors
   - ALWAYS drop and recreate tables in test cleanup - tests failed due to stale data
   - ALWAYS close sessions in finally blocks - caused session leaks
   - NEVER share sessions between tests - caused mysterious data issues

2. SQLAlchemy Relationship Issues:
   - Use lazy="joined" ONLY for small, frequently accessed relationships
   - Add .unique() when using joined loads to prevent duplicate rows
   - Refresh objects after adding relationships to see them
   - Use back_populates instead of backref for explicit relationships

3. SQLite Specific Issues:
   - Store booleans as INTEGER (0/1) - SQLite doesn't have true boolean type
   - Use check_same_thread=False for SQLite in tests
   - Use StaticPool for better test performance

4. Common Code Mistakes:
   - Don't over-engineer with pagination unless specifically needed
   - Don't add "helper" functions that duplicate SQLAlchemy features
   - Don't use Pydantic unless building an API
   - Use dataclasses for simple data transfer objects

5. Test Fixtures:
   - Use autouse=True for cleanup fixtures
   - Create complete test environment in each test
   - Don't assume database state from previous tests
   - Clean up ALL data, not just the data you created

6. Error Prevention:
   - Check if record exists before update/delete operations
   - Use try/finally for session cleanup
   - Always specify return types for clarity
   - Keep relationships simple - don't over-nest