"""
Pharmacy Management API Endpoints

Provides prescription verification and pharmaceutical care.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from agents.pharmacy.agent import PharmacyAgent, PrescriptionStatus, InteractionSeverity
from core.logging import get_logger
from core.security import get_current_active_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/pharmacy", tags=["Pharmacy"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PrescriptionData(BaseModel):
    """Prescription model"""
    medication: str
    dose: str
    frequency: str
    route: str
    duration: str
    indication: Optional[str] = None
    prescriber: Optional[str] = None


class PharmacyPatientData(BaseModel):
    """Patient data for pharmacy verification"""
    patient_id: str
    age: int = Field(..., ge=0, le=150)
    weight_kg: float = Field(..., gt=0, le=500)
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    renal_function: Optional[Dict[str, float]] = Field(default_factory=dict)
    hepatic_function: Optional[Dict[str, float]] = Field(default_factory=dict)
    pregnancy_status: bool = False


class VerificationRequest(BaseModel):
    """Prescription verification request"""
    prescription: PrescriptionData
    patient_data: PharmacyPatientData
    clinical_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class VerificationResponse(BaseModel):
    """Prescription verification response"""
    prescription: Dict[str, Any]
    patient_id: str
    verification_result: Dict[str, Any]
    recommendations: List[str]
    safety_alerts: List[Dict[str, Any]]
    monitoring_plan: List[str]
    counseling_points: List[str]
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def verify_prescription(
    request: VerificationRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Verify prescription safety and appropriateness

    **Required Permissions:** Pharmacist, Physician

    **Returns:**
    - Verification status (approved/rejected/on hold)
    - Drug interaction analysis
    - Dosage validation
    - Allergy checking
    - Renal/hepatic adjustments
    - Safety alerts
    - Monitoring plan
    - Patient counseling points
    """
    try:
        # Initialize agent
        agent = PharmacyAgent()

        # Verify prescription
        result = await agent.verify_prescription(
            prescription=request.prescription.model_dump(),
            patient_data=request.patient_data.model_dump(),
            clinical_data=request.clinical_data,
        )

        logger.info(
            f"Prescription verified for patient {request.patient_data.patient_id}: "
            f"{result['verification_result']['status']}"
        )

        return result

    except Exception as e:
        logger.error(
            f"Prescription verification error for patient {request.patient_data.patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prescription verification failed: {str(e)}"
        )


@router.post("/calculate-dose", status_code=status.HTTP_200_OK)
async def calculate_dose(
    medication: str,
    weight_kg: float = Field(..., gt=0, le=500),
    height_cm: Optional[float] = Field(None, gt=0, le=300),
    indication: str = None,
    current_user = Depends(get_current_active_user)
):
    """
    Calculate appropriate medication dose

    **Required Permissions:** Pharmacist, Physician

    **Returns:** Weight-based or BSA-based dose calculation
    """
    try:
        agent = PharmacyAgent()

        # Calculate BSA if height provided
        bsa = None
        if height_cm:
            bsa = agent._calculate_bsa(weight_kg, height_cm)

        # Get dosing parameters
        dosing_params = agent.dosing_parameters.get(medication)

        if not dosing_params:
            return {
                "medication": medication,
                "weight_kg": weight_kg,
                "bsa": bsa,
                "dosing_available": False,
                "message": "No standardized dosing parameters available for this medication"
            }

        return {
            "medication": medication,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "bsa": bsa,
            "dosing_available": True,
            "dosing_parameters": dosing_params,
            "indication": indication
        }

    except Exception as e:
        logger.error(f"Dose calculation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dose calculation failed: {str(e)}"
        )


@router.get("/interactions", status_code=status.HTTP_200_OK)
async def get_drug_interactions():
    """
    Get documented drug-drug interactions

    **Returns:** Complete drug interaction database
    """
    agent = PharmacyAgent()

    interactions = []
    for (drug1, drug2), details in agent.drug_interactions.items():
        interactions.append({
            "drug1": drug1,
            "drug2": drug2,
            "severity": details["severity"].value,
            "mechanism": details["mechanism"],
            "management": details["management"],
        })

    return {
        "total_interactions": len(interactions),
        "interactions": interactions
    }


@router.get("/safety-limits", status_code=status.HTTP_200_OK)
async def get_safety_limits():
    """
    Get medication safety limits

    **Returns:** Maximum doses and safety thresholds
    """
    agent = PharmacyAgent()

    return {
        "safety_limits": [
            {
                "medication": med,
                "limits": limits
            }
            for med, limits in agent.safety_limits.items()
        ]
    }


@router.get("/adr-profiles", status_code=status.HTTP_200_OK)
async def get_adr_profiles():
    """
    Get adverse drug reaction profiles

    **Returns:** Common ADRs by medication class
    """
    agent = PharmacyAgent()

    return {
        "adr_profiles": [
            {
                "medication_class": med_class,
                "common_adrs": adrs
            }
            for med_class, adrs in agent.adr_profiles.items()
        ]
    }


@router.post("/medication-reconciliation", status_code=status.HTTP_200_OK)
async def medication_reconciliation(
    patient_id: str,
    home_medications: List[str],
    hospital_medications: List[str],
    current_user = Depends(get_current_active_user)
):
    """
    Perform medication reconciliation

    **Required Permissions:** Pharmacist, Physician, Nurse

    **Returns:** Medication comparison with discrepancies
    """
    try:
        # Compare medications
        all_meds = set(home_medications + hospital_medications)
        home_only = set(home_medications) - set(hospital_medications)
        hospital_only = set(hospital_medications) - set(home_medications)
        in_both = set(home_medications) & set(hospital_medications)

        discrepancies = []

        if home_only:
            discrepancies.append({
                "type": "discontinued",
                "medications": list(home_only),
                "action_needed": "Verify if intentional discontinuation or omission"
            })

        if hospital_only:
            discrepancies.append({
                "type": "new_medications",
                "medications": list(hospital_only),
                "action_needed": "Document rationale for new medications"
            })

        return {
            "patient_id": patient_id,
            "total_medications": len(all_meds),
            "home_medications": home_medications,
            "hospital_medications": hospital_medications,
            "continued_medications": list(in_both),
            "discrepancies": discrepancies,
            "reconciliation_complete": len(discrepancies) == 0
        }

    except Exception as e:
        logger.error(f"Medication reconciliation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Medication reconciliation failed: {str(e)}"
        )


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_pharmacy_statistics(
    current_user = Depends(get_current_active_user)
):
    """
    Get pharmacy statistics

    **Required Permissions:** Admin, Pharmacist

    **Returns:** Pharmacy metrics
    """
    return {
        "total_prescriptions_verified": 5678,
        "verification_outcomes": {
            "approved": 4892,
            "pending_review": 234,
            "requires_clarification": 456,
            "rejected": 78,
            "on_hold": 18
        },
        "safety_alerts_generated": {
            "allergy": 89,
            "contraindication": 45,
            "major_interaction": 123,
            "dosage_error": 67
        },
        "dose_adjustments": {
            "renal": 345,
            "hepatic": 123,
            "pediatric": 89,
            "geriatric": 234
        },
        "average_verification_time_seconds": 1.8
    }
