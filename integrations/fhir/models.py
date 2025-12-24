"""
FHIR (Fast Healthcare Interoperability Resources) Models

Implements FHIR R4 standard for healthcare data interoperability.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# FHIR ENUMS
# ============================================================================

class FHIRResourceType(str, Enum):
    """FHIR resource types"""
    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    MEDICATION_REQUEST = "MedicationRequest"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    ENCOUNTER = "Encounter"
    PROCEDURE = "Procedure"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"


class ObservationStatus(str, Enum):
    """Observation status values"""
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"


class EncounterStatus(str, Enum):
    """Encounter status values"""
    PLANNED = "planned"
    ARRIVED = "arrived"
    IN_PROGRESS = "in-progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


# ============================================================================
# FHIR BASE MODELS
# ============================================================================

class FHIRIdentifier(BaseModel):
    """FHIR Identifier"""
    system: str = Field(..., description="Identity namespace (e.g., hospital ID system)")
    value: str = Field(..., description="Unique identifier value")
    use: Optional[str] = Field("official", description="usual | official | temp | secondary")


class FHIRReference(BaseModel):
    """FHIR Reference to another resource"""
    reference: str = Field(..., description="Relative or absolute URL reference")
    display: Optional[str] = Field(None, description="Text alternative for the resource")


class FHIRCoding(BaseModel):
    """FHIR Coding"""
    system: str = Field(..., description="Identity of the terminology system")
    code: str = Field(..., description="Symbol in syntax defined by the system")
    display: Optional[str] = Field(None, description="Representation defined by the system")


class FHIRCodeableConcept(BaseModel):
    """FHIR CodeableConcept"""
    coding: List[FHIRCoding] = Field(default_factory=list)
    text: Optional[str] = Field(None, description="Plain text representation")


class FHIRQuantity(BaseModel):
    """FHIR Quantity"""
    value: float
    unit: str
    system: Optional[str] = Field("http://unitsofmeasure.org", description="UCUM system")
    code: Optional[str] = None


class FHIRPeriod(BaseModel):
    """FHIR Period"""
    start: Optional[datetime] = None
    end: Optional[datetime] = None


# ============================================================================
# FHIR RESOURCE MODELS
# ============================================================================

class FHIRPatient(BaseModel):
    """FHIR Patient Resource"""
    resourceType: str = Field("Patient", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    # Name
    name: List[Dict[str, Any]] = Field(default_factory=list)

    # Demographics
    gender: Optional[str] = Field(None, description="male | female | other | unknown")
    birthDate: Optional[str] = None  # YYYY-MM-DD

    # Contact
    telecom: List[Dict[str, Any]] = Field(default_factory=list)
    address: List[Dict[str, Any]] = Field(default_factory=list)

    # Clinical
    active: bool = True


class FHIRObservation(BaseModel):
    """FHIR Observation Resource (Vital Signs, Lab Results)"""
    resourceType: str = Field("Observation", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    status: ObservationStatus
    category: List[FHIRCodeableConcept] = Field(default_factory=list)
    code: FHIRCodeableConcept  # What was observed (LOINC code)

    subject: FHIRReference  # Patient
    encounter: Optional[FHIRReference] = None

    # Result
    effectiveDateTime: Optional[datetime] = None
    valueQuantity: Optional[FHIRQuantity] = None
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None

    # Interpretation
    interpretation: Optional[List[FHIRCodeableConcept]] = Field(default_factory=list)


class FHIRCondition(BaseModel):
    """FHIR Condition Resource (Diagnosis)"""
    resourceType: str = Field("Condition", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    clinicalStatus: FHIRCodeableConcept
    verificationStatus: Optional[FHIRCodeableConcept] = None

    category: List[FHIRCodeableConcept] = Field(default_factory=list)
    severity: Optional[FHIRCodeableConcept] = None
    code: FHIRCodeableConcept  # Diagnosis code (ICD-10, SNOMED)

    subject: FHIRReference  # Patient
    encounter: Optional[FHIRReference] = None

    onsetDateTime: Optional[datetime] = None
    recordedDate: Optional[datetime] = None


class FHIRMedicationRequest(BaseModel):
    """FHIR MedicationRequest Resource (Prescription)"""
    resourceType: str = Field("MedicationRequest", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    status: str  # active | on-hold | cancelled | completed
    intent: str  # proposal | plan | order

    medicationCodeableConcept: FHIRCodeableConcept  # RxNorm code
    subject: FHIRReference  # Patient
    encounter: Optional[FHIRReference] = None

    authoredOn: Optional[datetime] = None
    requester: Optional[FHIRReference] = None

    # Dosage
    dosageInstruction: List[Dict[str, Any]] = Field(default_factory=list)


class FHIRDiagnosticReport(BaseModel):
    """FHIR DiagnosticReport Resource (Imaging, Lab Results)"""
    resourceType: str = Field("DiagnosticReport", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    status: str  # registered | partial | preliminary | final
    category: List[FHIRCodeableConcept] = Field(default_factory=list)
    code: FHIRCodeableConcept  # Report type (LOINC)

    subject: FHIRReference  # Patient
    encounter: Optional[FHIRReference] = None

    effectiveDateTime: Optional[datetime] = None
    issued: Optional[datetime] = None

    # Results
    result: List[FHIRReference] = Field(default_factory=list)  # Observations
    conclusion: Optional[str] = None


class FHIREncounter(BaseModel):
    """FHIR Encounter Resource (Patient Visit)"""
    resourceType: str = Field("Encounter", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    status: EncounterStatus
    class_: FHIRCoding = Field(..., alias="class")  # ambulatory | emergency | inpatient

    type: List[FHIRCodeableConcept] = Field(default_factory=list)
    subject: FHIRReference  # Patient
    participant: List[Dict[str, Any]] = Field(default_factory=list)

    period: Optional[FHIRPeriod] = None
    reasonCode: List[FHIRCodeableConcept] = Field(default_factory=list)

    # Location
    location: List[Dict[str, Any]] = Field(default_factory=list)


class FHIRAllergyIntolerance(BaseModel):
    """FHIR AllergyIntolerance Resource"""
    resourceType: str = Field("AllergyIntolerance", const=True)
    id: Optional[str] = None
    identifier: List[FHIRIdentifier] = Field(default_factory=list)

    clinicalStatus: Optional[FHIRCodeableConcept] = None
    verificationStatus: Optional[FHIRCodeableConcept] = None

    type: Optional[str] = Field(None, description="allergy | intolerance")
    category: List[str] = Field(default_factory=list)  # food | medication | environment | biologic

    criticality: Optional[str] = Field(None, description="low | high | unable-to-assess")
    code: Optional[FHIRCodeableConcept] = None  # Substance code

    patient: FHIRReference
    recordedDate: Optional[datetime] = None

    reaction: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# FHIR BUNDLE (Collection of Resources)
# ============================================================================

class FHIRBundleEntry(BaseModel):
    """FHIR Bundle Entry"""
    fullUrl: Optional[str] = None
    resource: Dict[str, Any]


class FHIRBundle(BaseModel):
    """FHIR Bundle - Collection of resources"""
    resourceType: str = Field("Bundle", const=True)
    id: Optional[str] = None
    type: str  # document | message | transaction | collection | searchset | history

    timestamp: Optional[datetime] = None
    total: Optional[int] = None
    entry: List[FHIRBundleEntry] = Field(default_factory=list)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_patient_identifier(patient_id: str, system: str = "http://hospital.com/patient") -> FHIRIdentifier:
    """Create FHIR patient identifier"""
    return FHIRIdentifier(system=system, value=patient_id, use="official")


def create_observation_vital_sign(
    patient_id: str,
    code: str,
    display: str,
    value: float,
    unit: str,
    system: str = "http://loinc.org"
) -> FHIRObservation:
    """
    Create FHIR Observation for vital sign

    Args:
        patient_id: Patient ID
        code: LOINC code
        display: Display name
        value: Measured value
        unit: Unit of measurement

    Returns:
        FHIRObservation instance
    """
    return FHIRObservation(
        status=ObservationStatus.FINAL,
        category=[
            FHIRCodeableConcept(
                coding=[
                    FHIRCoding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="vital-signs",
                        display="Vital Signs"
                    )
                ]
            )
        ],
        code=FHIRCodeableConcept(
            coding=[FHIRCoding(system=system, code=code, display=display)],
            text=display
        ),
        subject=FHIRReference(reference=f"Patient/{patient_id}"),
        effectiveDateTime=datetime.utcnow(),
        valueQuantity=FHIRQuantity(value=value, unit=unit)
    )


def create_condition_diagnosis(
    patient_id: str,
    code: str,
    display: str,
    system: str = "http://snomed.info/sct"
) -> FHIRCondition:
    """
    Create FHIR Condition for diagnosis

    Args:
        patient_id: Patient ID
        code: SNOMED CT or ICD-10 code
        display: Display name
        system: Coding system

    Returns:
        FHIRCondition instance
    """
    return FHIRCondition(
        clinicalStatus=FHIRCodeableConcept(
            coding=[
                FHIRCoding(
                    system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    code="active",
                    display="Active"
                )
            ]
        ),
        code=FHIRCodeableConcept(
            coding=[FHIRCoding(system=system, code=code, display=display)],
            text=display
        ),
        subject=FHIRReference(reference=f"Patient/{patient_id}"),
        recordedDate=datetime.utcnow()
    )
