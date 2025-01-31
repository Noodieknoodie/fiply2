# backend\database_operations\connection.py
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

# Get the absolute path to the database file
DB_PATH = Path(__file__).parent / "database" / "fiply2_database.db"

def get_engine() -> Engine:
    """Create and return a SQLAlchemy engine instance."""
    # Create database directory if it doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Create SQLite database engine with 2.0 style
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        echo=False,  # Set to True for SQL query logging
        future=True,  # Use SQLAlchemy 2.0 style
        poolclass=StaticPool,  # Better for SQLite
        connect_args={"check_same_thread": False}  # Allow multi-threading for SQLite
    )
    return engine

def get_session() -> Session:
    """Create and return a new database session."""
    engine = get_engine()
    # 2.0 style session creation
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        future=True  # Use 2.0 style
    )
    return SessionLocal()

# Create database and tables on import if they don't exist
engine = get_engine()
