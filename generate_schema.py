import os
from pathlib import Path
from sqlalchemy.schema import CreateTable
from sqlalchemy import create_engine
from backend.database_operations.models import Base


# Define paths correctly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # Most parent root (fiply2/)
BACKEND_DIR = Path(__file__).resolve().parent.parent  # Backend directory
DB_PATH = BACKEND_DIR / "database_operations" / "database" / "fiply.db"
SCHEMA_SQL_PATH = BACKEND_DIR / "database_operations" / "database" / "schema.sql"
SCHEMA_MD_PATH = PROJECT_ROOT / "FIPLI_DB_SCHEMA.md"  # Root directory

# Create engine
engine = create_engine(f"sqlite:///{DB_PATH}")

def generate_schema():
    # Ensure schema.sql path exists
    SCHEMA_SQL_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_SQL_PATH, 'w', encoding='utf-8') as f:
        f.write('-- Generated schema from SQLAlchemy models\n\n')
        
        metadata = Base.metadata
        for table in sorted(metadata.tables.values(), key=lambda t: t.name):
            f.write(f'{str(CreateTable(table).compile(engine))};\n\n')

    update_schema_md()

def update_schema_md():
    # Read first 10 lines of FIPLI_DB_SCHEMA.md if it exists
    if SCHEMA_MD_PATH.exists():
        with open(SCHEMA_MD_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        preserved = lines[:10] if len(lines) >= 10 else lines
    else:
        preserved = []

    # Overwrite FIPLI_DB_SCHEMA.md while keeping the first 10 lines
    with open(SCHEMA_MD_PATH, 'w', encoding='utf-8') as f:
        f.writelines(preserved)
        f.write('\n-- Updated Schema Below --\n\n')
        with open(SCHEMA_SQL_PATH, 'r', encoding='utf-8') as schema_file:
            f.write(schema_file.read())

if __name__ == '__main__':
    generate_schema()
