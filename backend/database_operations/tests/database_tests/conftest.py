"""Test configuration and shared fixtures."""

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ...models import Base
from ...calculations.base_facts import (
    GrowthConfig,
    GrowthType,
    TimeRange
)

@pytest.fixture
def db_session():
    """Create a new database session for a test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def sample_growth_config():
    """Create a sample growth configuration for testing."""
    today = date.today()
    return GrowthConfig(
        rate=0.07,
        config_type=GrowthType.OVERRIDE,
        time_range=TimeRange(
            start_date=today,
            end_date=None
        )
    )

@pytest.fixture
def sample_stepwise_growth_config():
    """Create a sample stepwise growth configuration for testing."""
    today = date.today()
    return [
        GrowthConfig(
            rate=0.08,
            config_type=GrowthType.STEPWISE,
            time_range=TimeRange(
                start_date=today,
                end_date=date(today.year + 2, today.month, today.day)
            )
        ),
        GrowthConfig(
            rate=0.06,
            config_type=GrowthType.STEPWISE,
            time_range=TimeRange(
                start_date=date(today.year + 2, today.month, today.day + 1),
                end_date=None
            )
        )
    ] 