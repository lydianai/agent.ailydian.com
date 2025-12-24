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


class UserRole(str, enum.Enum):
    """User roles with different permissions"""
    ADMIN = "admin"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    RADIOLOGIST = "radiologist"
    PHARMACIST = "pharmacist"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class SubscriptionTier(str, enum.Enum):
    """Hospital subscription tiers"""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM_PLUS = "quantum_plus"


class ComplianceRegion(str, enum.Enum):
    """Regulatory compliance regions"""
    USA = "usa"  # HIPAA
    EU = "eu"  # GDPR
    TURKEY = "turkey"  # KVKK
    JAPAN = "japan"  # PMDA
    MIDDLE_EAST = "middle_east"  # SFDA


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


# ============================================================================
# HOSPITAL MODEL (Multi-Tenant)
# ============================================================================

class Hospital(Base):
    """
    Hospital/Healthcare Organization Model

    Provides multi-tenant isolation for the platform.
    Each hospital is a separate tenant with isolated data.
    """
    __tablename__ = "hospitals"

    # Primary Key
    hospital_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Basic Info
    name = Column(String(200), nullable=False)
    tenant_id = Column(String(100), unique=True, nullable=False, index=True)

    # Location
    country = Column(String(2))  # ISO 3166-1 alpha-2
    state = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    timezone = Column(String(50), default="UTC")

    # Contact
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))

    # Integration
    fhir_endpoint = Column(String(500))  # Epic/Cerner FHIR endpoint
    fhir_client_id = Column(String(200))
    fhir_client_secret_encrypted = Column(LargeBinary)
    ehr_system = Column(String(50))  # "epic", "cerner", "custom"

    # Subscription
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.COMMUNITY)
    subscription_start_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))
    monthly_fee = Column(Float, default=0.0)

    # Compliance
    compliance_region = Column(SQLEnum(ComplianceRegion), nullable=False)
    hipaa_compliant = Column(Boolean, default=False)
    gdpr_compliant = Column(Boolean, default=False)
    kvkk_compliant = Column(Boolean, default=False)

    # Limits (based on subscription)
    max_patients = Column(Integer)  # null = unlimited
    max_users = Column(Integer)
    max_ai_requests_per_day = Column(Integer)
    quantum_enabled = Column(Boolean, default=False)

    # Settings
    settings = Column(JSONB, default={})  # Hospital-specific configurations

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="hospital")

    __table_args__ = (
        Index("idx_hospital_tenant", "tenant_id"),
        Index("idx_hospital_active", "is_active"),
    )


# ============================================================================
# USER MODEL (Authentication & Authorization)
# ============================================================================

class User(Base):
    """
    User Model with Role-Based Access Control

    Replaces hardcoded mock users with real database-backed authentication.
    Supports MFA, session management, and comprehensive audit logging.
    """
    __tablename__ = "users"

    # Primary Key
    user_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Hospital (Multi-Tenant)
    hospital_id = Column(PGUUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), nullable=False, index=True)

    # Authentication
    email = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # bcrypt hash

    # Personal Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200))  # Computed: first_name + last_name

    # Role & Permissions
    role = Column(SQLEnum(UserRole), nullable=False)
    permissions = Column(JSONB, default={})  # Granular permissions

    # Medical License (for clinical staff)
    medical_license_number = Column(String(50))
    medical_license_state = Column(String(50))
    medical_specialties = Column(ARRAY(String))  # ["cardiology", "internal_medicine"]

    # Contact
    phone = Column(String(20))
    phone_verified = Column(Boolean, default=False)

    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32))  # TOTP secret
    mfa_backup_codes = Column(ARRAY(String))  # Encrypted backup codes

    # Security
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    email_verification_token = Column(String(255))
    email_verified = Column(Boolean, default=False)

    # Session Management
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(45))  # IPv6 max length
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))  # Account lockout

    # Preferences
    preferred_language = Column(String(5), default="en")  # ISO 639-1
    timezone = Column(String(50), default="UTC")
    theme = Column(String(20), default="dark")  # "dark", "light"

    # Notifications
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True))  # Who created this user
    last_password_change = Column(DateTime(timezone=True))

    # Relationships
    hospital = relationship("Hospital", back_populates="users")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_hospital", "hospital_id"),
        Index("idx_user_role", "role"),
        Index("idx_user_active", "is_active"),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'", name="valid_email"),
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"


# ============================================================================
# USER SESSION MODEL (JWT Token Tracking)
# ============================================================================

class UserSession(Base):
    """
    Active user sessions for JWT token management

    Enables token revocation and session tracking.
    """
    __tablename__ = "user_sessions"

    session_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)

    # JWT Token Info
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID
    access_token_hash = Column(String(64))  # SHA256 hash for quick lookup
    refresh_token_hash = Column(String(64))

    # Session Metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_type = Column(String(50))  # "mobile", "desktop", "tablet"
    device_name = Column(String(100))

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(200))

    __table_args__ = (
        Index("idx_session_user", "user_id"),
        Index("idx_session_jti", "jti"),
        Index("idx_session_expires", "expires_at"),
    )


# ============================================================================
# AUDIT LOG MODEL (HIPAA Compliance)
# ============================================================================

class AuditLog(Base):
    """
    Comprehensive audit log for HIPAA compliance

    Tracks all user actions, data access, and system events.
    WORM (Write-Once-Read-Many) - records cannot be modified or deleted.
    """
    __tablename__ = "audit_logs"

    log_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Who
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    hospital_id = Column(PGUUID(as_uuid=True), ForeignKey("hospitals.hospital_id"), index=True)

    # What
    action = Column(String(100), nullable=False)  # "patient.view", "medication.prescribe"
    resource_type = Column(String(50))  # "patient", "medication", "vital_signs"
    resource_id = Column(String(100))

    # Details
    description = Column(Text)
    metadata = Column(JSONB)  # Full context

    # When & Where
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Outcome
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # PHI Access (HIPAA specific)
    accessed_phi = Column(Boolean, default=False)
    phi_fields = Column(ARRAY(String))  # Which PHI fields were accessed

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )
