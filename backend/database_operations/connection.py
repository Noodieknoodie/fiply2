# backend\database_operations\connection.py
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from .models import init_tables

# Get the absolute path to the database file
DB_PATH = Path(__file__).parent / "database" / "fiply2_database.db"

# Global engine instance
_engine = None

def init_database() -> Engine:
    """Initialize the database engine and tables. Call this once when your application starts."""
    global _engine
    if _engine is None:
        # Create database directory if it doesn't exist
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create SQLite database engine with 2.0 style
        _engine = create_engine(
            f"sqlite:///{DB_PATH}",
            echo=False,  # Set to True for SQL query logging
            future=True,  # Use SQLAlchemy 2.0 style
            poolclass=StaticPool,  # Better for SQLite
            connect_args={"check_same_thread": False}  # Allow multi-threading for SQLite
        )
        
        # Initialize tables
        init_tables(_engine)
        
    return _engine

def get_engine() -> Engine:
    """Get the database engine. Make sure init_database() was called first."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine

def get_session() -> Session:
    """Create and return a new database session."""
    engine = get_engine()  # This will raise an error if init_database() wasn't called
    # 2.0 style session creation
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        future=True  # Use 2.0 style
    )
    return SessionLocal()

