"""Database module"""

from .models import (
    Base, Patient, Physician, Encounter, VitalSign, Medication,
    AgentDecision, Alert,
    Gender, EncounterType, MedicationStatus, AlertSeverity, DecisionOutcome
)
from .connection import (
    get_db, async_engine, AsyncSessionLocal,
    mongodb, redis_cache,
    init_databases, close_databases
)

__all__ = [
    # Models
    "Base", "Patient", "Physician", "Encounter", "VitalSign", "Medication",
    "AgentDecision", "Alert",
    # Enums
    "Gender", "EncounterType", "MedicationStatus", "AlertSeverity", "DecisionOutcome",
    # Database
    "get_db", "async_engine", "AsyncSessionLocal",
    "mongodb", "redis_cache",
    "init_databases", "close_databases"
]
