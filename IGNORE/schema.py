import sqlite3

db_path = "C:\\CORE FOLDERS\\FIPLY2\\backend\\database_operations\\database\\fiply2_database.db"
schema_path = "C:\\CORE FOLDERS\\FIPLY2\\backend\\database_operations\\database\\schema.sql"

# List of tables in the specified order
tables = [
    "households", "plans", "base_assumptions", "scenarios", "scenario_assumptions",
    "scenario_overrides", "asset_categories", "assets", "liability_categories", "liabilities",
    "inflows_outflows", "retirement_income_plans", "growth_rate_configurations"
]

def get_table_dump(cursor, table_name):
    """Retrieve the full dump for a specific table."""
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    return result[0] if result and result[0] else f"-- No schema found for {table_name}"

def get_index_schemas(cursor):
    """Retrieve all index schemas."""
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    return [row[0] for row in cursor.fetchall()]

def main():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Extract schemas
        schema_statements = ["-- SQLite Database Schema\n"]
        for table in tables:
            schema_statements.append(f"-- Schema for {table}\n")
            schema_statements.append(get_table_dump(cursor, table) + "\n")
        
        # Extract indexes
        schema_statements.append("-- Indexes\n")
        index_statements = get_index_schemas(cursor)
        schema_statements.extend(index_statements)
        
        # Write to file (overwrite mode)
        with open(schema_path, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
    
    print(f"Schema successfully written to {schema_path}")

if __name__ == "__main__":
    main()
