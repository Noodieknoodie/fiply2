# tests/test_timeline_validation.py
from database_operations.validation.scenario_timeline_validation import validate_projection_timeline

def test_validate_projection_timeline(db_session):
    """Test timeline validation prevents impossible sequences"""
    assert validate_projection_timeline(2024, 2040, 2060) == True

    assert validate_projection_timeline(2024, 2025, 2020) == False  # End before retirement
    assert validate_projection_timeline(2030, 2025, 2040) == False  # Retirement before start

