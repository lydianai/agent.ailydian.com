"""
Emergency Response Agent Module

Provides emergency triage and critical decision support.
"""

from agents.emergency_response.agent import (
    EmergencyResponseAgent,
    TriageLevel,
    EmergencyType,
)

__all__ = [
    "EmergencyResponseAgent",
    "TriageLevel",
    "EmergencyType",
]
