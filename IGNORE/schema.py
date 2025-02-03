import os
import sqlite3

# Dynamically locate the project root (two levels up from IGNORE/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Correct database and schema paths
DB_PATH = os.path.join(PROJECT_ROOT, "backend", "database_operations", "database", "fiply2_database.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "backend", "database_operations", "database", "schema.sql")
FIPLI_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "docs", "FIPLI_DB_SCHEMA.md")
FIPLI_DATA_DUMP_PATH = os.path.join(PROJECT_ROOT, "backend", "database_operations", "database", "data_dump.sql")

# Verify that the database exists before running
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Database file not found: {DB_PATH}")

TABLES = [
    "households", "plans", "base_assumptions", "scenarios", "scenario_assumptions",
    "scenario_overrides", "asset_categories", "assets", "liability_categories", "liabilities",
    "inflows_outflows", "retirement_income_plans", "growth_rate_configurations"
]

def fetch_schema(cursor, table_name):
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()
    return result[0] if result and result[0] else f"-- No schema found for {table_name}"

def fetch_indexes(cursor):
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    return [row[0] for row in cursor.fetchall()]

def export_schema():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        schema_content = ["-- SQLite Database Schema\n"]
        
        for table in TABLES:
            schema_content.append(f"-- Schema for {table}\n")
            schema_content.append(fetch_schema(cursor, table) + "\n")

        indexes = fetch_indexes(cursor)
        if indexes:
            schema_content.append("-- Indexes\n" + "\n".join(indexes) + "\n")

        schema_text = "\n".join(schema_content)

        # Overwrite schema.sql completely
        with open(SCHEMA_PATH, "w", encoding="utf-8") as schema_file:
            schema_file.write(schema_text)

        # Ensure docs/FIPLI_DB_SCHEMA.md exists and has 10 reserved rows
        if not os.path.exists(FIPLI_SCHEMA_PATH):
            with open(FIPLI_SCHEMA_PATH, "w", encoding="utf-8") as f:
                f.write("\n" * 9)  # Ensure at least 9 blank rows

        # Read top 10 lines from FIPLI_DB_SCHEMA.md and preserve them
        with open(FIPLI_SCHEMA_PATH, "r+", encoding="utf-8") as f:
            existing_lines = f.readlines()

            while len(existing_lines) < 9:
                existing_lines.append("\n")  # Ensure exactly 9 blank rows

            f.seek(0)
            f.writelines(existing_lines[:9])  # Keep first 9 lines intact
            f.write("\n")  # Add the 10th line for separation
            f.write(schema_text)  # Write new schema content


        data_dump_content = ["-- SQLite Database Data Dump\n"]
        for line in conn.iterdump():
            if not line.startswith("CREATE TABLE sqlite_sequence") and "INSERT INTO sqlite_sequence" not in line:
                data_dump_content.append(line + "\n")

        with open(FIPLI_DATA_DUMP_PATH, "w", encoding="utf-8") as data_dump_file:
            data_dump_file.writelines(data_dump_content)

if __name__ == "__main__":
    export_schema()
    print(f"Schema exported to:\n - {SCHEMA_PATH}\n - {FIPLI_SCHEMA_PATH}\n - {FIPLI_DATA_DUMP_PATH}")
