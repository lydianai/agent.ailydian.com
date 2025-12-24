"""
Database Models (SQLAlchemy)

HIPAA-compliant data models with encryption for PHI.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey,
    Text, LargeBinary, Index, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class EncounterType(str, enum.Enum):
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"
    EMERGENCY = "emergency"
    TELEMEDICINE = "telemedicine"


class MedicationStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    CRITICAL = "critical"


class DecisionOutcome(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    NEEDS_REVIEW = "needs_review"


# ============================================================================
# PATIENT MODEL
# ============================================================================

class Patient(Base):
    """
    Patient model with encrypted PHI

    PHI fields (first_name, last_name, ssn, dob) are stored encrypted.
    """
    __tablename__ = "patients"

    # Primary Key
    patient_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Medical Record Number (searchable, unique)
    mrn = Column(String(50), unique=True, nullable=False, index=True)

    # Encrypted PHI (stored as binary)
    first_name_encrypted = Column(LargeBinary, nullable=False)
    last_name_encrypted = Column(LargeBinary, nullable=False)
    ssn_encrypted = Column(LargeBinary)
    dob_encrypted = Column(LargeBinary, nullable=False)

    # Demographics (non-PHI after aggregation)
    age_range = Column(String(10))  # "30-40", "40-50" (HIPAA Safe Harbor)
    gender = Column(SQLEnum(Gender), nullable=False)
    ethnicity = Column(String(50))
    preferred_language = Column(String(20), default="en")

    # Clinical
    blood_type = Column(String(5))
    allergies = Column(JSONB)  # [{drug: "penicillin", severity: "severe"}]

    # Administrative
    insurance_provider = Column(String(100))
    primary_care_physician_id = Column(PGUUID(as_uuid=True), ForeignKey("physicians.physician_id"))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True))

    # Soft delete
    deleted_at = Column(DateTime(timezone=True))

    # Encryption metadata
    encryption_key_version = Column(Integer, nullable=False, default=1)

    # Relationships
    encounters = relationship("Encounter", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    vital_signs = relationship("VitalSign", back_populates="patient")

    __table_args__ = (
        Index("idx_patient_mrn", "mrn"),
        Index("idx_patient_created", "created_at"),
    )


# ============================================================================
# PHYSICIAN MODEL
# ============================================================================

class Physician(Base):
    """Physician/Provider model"""
    __tablename__ = "physicians"

    physician_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Credentials
    npi = Column(String(10), unique=True, nullable=False)  # National Provider Identifier
    license_number = Column(String(50))
    specialty = Column(String(100))

    # Personal info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patients = relationship("Patient", back_populates="primary_care_physician")


# Placeholder for relationship
Patient.primary_care_physician = relationship("Physician", back_populates="patients")


# ============================================================================
# ENCOUNTER MODEL
# ============================================================================

class Encounter(Base):
    """Hospital encounter/visit"""
    __tablename__ = "encounters"

    encounter_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False)

    # Encounter details
    encounter_type = Column(SQLEnum(EncounterType), nullable=False)
    admission_timestamp = Column(DateTime(timezone=True), nullable=False)
    discharge_timestamp = Column(DateTime(timezone=True))

    # Location
    hospital_id = Column(PGUUID(as_uuid=True))
    department = Column(String(100))
    room_bed = Column(String(20))

    # Clinical
    chief_complaint = Column(Text)
    admitting_diagnosis = Column(String(200))
    discharge_diagnosis = Column(String(200))

    # Assigned staff
    attending_physician_id = Column(PGUUID(as_uuid=True), ForeignKey("physicians.physician_id"))
    assigned_nurses = Column(ARRAY(PGUUID(as_uuid=True)))

    # Billing
    total_charges = Column(Float)
    insurance_payments = Column(Float)
    patient_responsibility = Column(Float)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    vital_signs = relationship("VitalSign", back_populates="encounter")
    medications = relationship("Medication", back_populates="encounter")

    __table_args__ = (
        Index("idx_encounter_patient", "patient_id"),
        Index("idx_encounter_admission", "admission_timestamp"),
    )


# ============================================================================
# VITAL SIGNS MODEL (Time-Series)
# ============================================================================

class VitalSign(Base):
    """
    Vital signs measurements

    High-frequency time-series data (stored in TimescaleDB hypertable)
    """
    __tablename__ = "vital_signs"

    measurement_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False)
    encounter_id = Column(PGUUID(as_uuid=True), ForeignKey("encounters.encounter_id"))

    measured_at = Column(DateTime(timezone=True), nullable=False)

    # Vitals
    heart_rate = Column(Integer)  # bpm
    blood_pressure_systolic = Column(Integer)  # mmHg
    blood_pressure_diastolic = Column(Integer)  # mmHg
    respiratory_rate = Column(Integer)  # breaths/min
    oxygen_saturation = Column(Float)  # %
    temperature = Column(Float)  # Celsius

    # Source
    measurement_device = Column(String(100))
    measured_by = Column(PGUUID(as_uuid=True))

    # Quality
    is_validated = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="vital_signs")
    encounter = relationship("Encounter", back_populates="vital_signs")

    __table_args__ = (
        Index("idx_vitals_patient_time", "patient_id", "measured_at"),
        Index("idx_vitals_measured_at", "measured_at"),
    )


# ============================================================================
# MEDICATION MODEL
# ============================================================================

class Medication(Base):
    """Patient medications"""
    __tablename__ = "medications"

    medication_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False)
    encounter_id = Column(PGUUID(as_uuid=True), ForeignKey("encounters.encounter_id"))

    # Drug info
    drug_name = Column(String(200), nullable=False)
    generic_name = Column(String(200))
    rxnorm_code = Column(String(50))  # RxNorm code for standardization

    # Dosage
    dose = Column(Float)
    dose_unit = Column(String(50))
    route = Column(String(50))  # oral, IV, IM, etc.
    frequency = Column(String(50))  # QID, BID, PRN, etc.

    # Timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))

    # Prescriber
    prescribed_by = Column(PGUUID(as_uuid=True), ForeignKey("physicians.physician_id"))

    # Status
    status = Column(SQLEnum(MedicationStatus), default=MedicationStatus.ACTIVE)

    # Safety checks
    allergy_checked = Column(Boolean, default=False)
    interaction_checked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="medications")
    encounter = relationship("Encounter", back_populates="medications")

    __table_args__ = (
        Index("idx_medication_patient", "patient_id"),
        Index("idx_medication_status", "status"),
    )


# ============================================================================
# AGENT DECISION MODEL
# ============================================================================

class AgentDecision(Base):
    """
    AI Agent decisions (audit trail)

    Stores all agent decisions for compliance and learning.
    """
    __tablename__ = "agent_decisions"

    decision_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Agent info
    agent_type = Column(String(50), nullable=False)  # clinical_decision, resource_optimization
    agent_version = Column(String(20), nullable=False)

    # Context
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id"))
    encounter_id = Column(PGUUID(as_uuid=True), ForeignKey("encounters.encounter_id"))

    # Input
    input_data = Column(JSONB, nullable=False)  # Full input to agent

    # Decision
    decision_type = Column(String(50), nullable=False)  # diagnosis, treatment_plan, schedule
    decision_output = Column(JSONB, nullable=False)
    confidence_score = Column(Float)

    # Reasoning
    reasoning_steps = Column(JSONB)  # Chain-of-thought
    knowledge_sources = Column(JSONB)  # Citations

    # Safety
    guardrails_applied = Column(JSONB)
    human_review_required = Column(Boolean, default=False)
    human_reviewed_by = Column(PGUUID(as_uuid=True))
    human_review_timestamp = Column(DateTime(timezone=True))
    human_approval_status = Column(String(20))  # approved, rejected, modified

    # Outcome tracking (for learning)
    actual_outcome = Column(JSONB)
    outcome_recorded_at = Column(DateTime(timezone=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Compliance (WORM - Write Once Read Many)
    is_immutable = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_agent_decision_patient", "patient_id"),
        Index("idx_agent_decision_created", "created_at"),
        Index("idx_agent_decision_type", "agent_type", "decision_type"),
        Index("idx_agent_decision_output_gin", "decision_output", postgresql_using="gin"),
    )


# ============================================================================
# ALERT MODEL
# ============================================================================

class Alert(Base):
    """Patient alerts from monitoring agents"""
    __tablename__ = "alerts"

    alert_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False)
    encounter_id = Column(PGUUID(as_uuid=True), ForeignKey("encounters.encounter_id"))

    # Alert details
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    alert_type = Column(String(50), nullable=False)  # sepsis_risk, fall_detected, vitals_anomaly
    message = Column(Text, nullable=False)
    details = Column(JSONB)

    # Recommended action
    recommended_action = Column(Text)
    escalate_to = Column(ARRAY(String))  # Roles to notify

    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(PGUUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))

    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(PGUUID(as_uuid=True))
    resolved_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_alert_patient", "patient_id"),
        Index("idx_alert_severity", "severity"),
        Index("idx_alert_created", "created_at"),
    )
