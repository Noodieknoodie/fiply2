import os
from pathlib import Path
from sqlalchemy.schema import CreateTable
from sqlalchemy import create_engine
from models import Base

# Get the path to the actual database file
DB_PATH = Path(__file__).parent / "database" / "fiply2_database.db"

# Create engine using the actual database
engine = create_engine(f"sqlite:///{DB_PATH}")

def generate_schema():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Open schema.sql file in the same directory
    schema_path = os.path.join(script_dir, 'schema.sql')
    with open(schema_path, 'w') as f:
        # Write header comment
        f.write('-- Generated schema from SQLAlchemy models\n\n')
        
        # Get all tables from metadata
        metadata = Base.metadata
        
        # Sort tables by name for consistency
        for table in sorted(metadata.tables.values(), key=lambda t: t.name):
            # Convert the CreateTable construct to a string
            create_table = str(CreateTable(table).compile(engine))
            
            # Write the create table statement
            f.write(f'{create_table};\n\n')

if __name__ == '__main__':
    generate_schema() 