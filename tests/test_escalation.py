"""
Tests – Escalation Service
All boundary cases for the tone stage resolver.
"""

import pytest
from src.Smart_Credit_Orchestrator.services.escalation_service import resolve_stage


@pytest.mark.parametrize("days,expected_stage,expected_escalated", [
    (0,  1, False),   # just overdue
    (1,  1, False),   # Stage 1 lower
    (7,  1, False),   # Stage 1 upper
    (8,  2, False),   # Stage 2 lower
    (14, 2, False),   # Stage 2 upper
    (15, 3, False),   # Stage 3 lower
    (21, 3, False),   # Stage 3 upper
    (22, 4, False),   # Stage 4 lower
    (30, 4, False),   # Stage 4 upper
    (31, 4, True),    # Escalation threshold
    (60, 4, True),    # Well beyond threshold
])
def test_resolve_stage(days, expected_stage, expected_escalated):
    stage, escalated = resolve_stage(days)
    assert stage == expected_stage, f"days={days}: expected stage {expected_stage}, got {stage}"
    assert escalated == expected_escalated, f"days={days}: expected escalated={expected_escalated}"


def test_boundary_30_is_not_escalated():
    _, escalated = resolve_stage(30)
    assert escalated is False


def test_boundary_31_is_escalated():
    _, escalated = resolve_stage(31)
    assert escalated is True
