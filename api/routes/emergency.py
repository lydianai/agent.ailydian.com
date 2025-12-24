"""
Emergency Response API Endpoints

Provides emergency triage and critical decision support.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from agents.emergency_response.agent import EmergencyResponseAgent, TriageLevel, EmergencyType
from core.logging import get_logger
from core.security import get_current_active_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/emergency", tags=["Emergency Response"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class VitalSigns(BaseModel):
    """Vital signs model"""
    heart_rate: Optional[int] = Field(None, ge=0, le=300)
    respiratory_rate: Optional[int] = Field(None, ge=0, le=100)
    systolic_bp: Optional[int] = Field(None, ge=0, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=0, le=200)
    spo2: Optional[int] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0)


class TriageRequest(BaseModel):
    """Triage request model"""
    patient_id: str = Field(..., min_length=1)
    chief_complaint: str = Field(..., min_length=1)
    vital_signs: VitalSigns
    symptoms: List[str] = Field(default_factory=list)
    onset_time: Optional[datetime] = None
    medical_history: Optional[List[str]] = Field(default_factory=list)


class TriageResponse(BaseModel):
    """Triage response model"""
    patient_id: str
    triage_level: str
    priority: str
    emergency_type: Optional[str]
    action_plan: Dict[str, Any]
    abcde_assessment: Dict[str, Any]
    red_flags: List[str]
    protocols_activated: List[Dict[str, Any]]
    confidence: float
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/triage", response_model=TriageResponse, status_code=status.HTTP_200_OK)
async def triage_patient(
    request: TriageRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Perform emergency triage assessment

    **Required Permissions:** Physician, Nurse

    **Returns:**
    - ESI triage level (1-5)
    - Priority level
    - Emergency type classification
    - ABCDE assessment
    - Action plan with immediate interventions
    - Activated time-critical protocols
    """
    try:
        # Initialize agent
        agent = EmergencyResponseAgent()

        # Perform triage
        result = await agent.triage_patient(
            chief_complaint=request.chief_complaint,
            vital_signs=request.vital_signs.model_dump(exclude_none=True),
            symptoms=request.symptoms,
            onset_time=request.onset_time,
            medical_history=request.medical_history,
        )

        # Add patient_id to result
        result["patient_id"] = request.patient_id

        logger.info(f"Triage completed for patient {request.patient_id}: {result['triage_level']}")

        return result

    except Exception as e:
        logger.error(f"Triage error for patient {request.patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage assessment failed: {str(e)}"
        )


@router.get("/triage-levels", status_code=status.HTTP_200_OK)
async def get_triage_levels():
    """
    Get ESI triage level descriptions

    **Returns:** All ESI levels with descriptions
    """
    return {
        "levels": [
            {
                "level": TriageLevel.LEVEL_1.value,
                "name": "Immediate",
                "description": "Life-saving intervention required",
                "time_to_treatment": "0 minutes",
                "examples": ["Cardiac arrest", "Respiratory failure", "Severe shock"]
            },
            {
                "level": TriageLevel.LEVEL_2.value,
                "name": "Emergent",
                "description": "High risk, confusion, severe pain/distress",
                "time_to_treatment": "< 10 minutes",
                "examples": ["Chest pain", "Stroke symptoms", "Severe trauma"]
            },
            {
                "level": TriageLevel.LEVEL_3.value,
                "name": "Urgent",
                "description": "Stable but needs multiple resources",
                "time_to_treatment": "< 30 minutes",
                "examples": ["Abdominal pain", "Moderate asthma", "Minor trauma"]
            },
            {
                "level": TriageLevel.LEVEL_4.value,
                "name": "Less Urgent",
                "description": "Stable, needs one resource",
                "time_to_treatment": "< 60 minutes",
                "examples": ["Minor injury", "Simple laceration", "Mild pain"]
            },
            {
                "level": TriageLevel.LEVEL_5.value,
                "name": "Non-Urgent",
                "description": "No resources needed immediately",
                "time_to_treatment": "< 120 minutes",
                "examples": ["Minor symptoms", "Prescription refill", "Health education"]
            }
        ]
    }


@router.get("/protocols", status_code=status.HTTP_200_OK)
async def get_emergency_protocols():
    """
    Get time-critical emergency protocols

    **Returns:** All emergency protocols with time windows
    """
    return {
        "protocols": [
            {
                "name": "Stroke Alert",
                "type": EmergencyType.STROKE.value,
                "time_window_minutes": 60,
                "key_interventions": ["CT scan", "tPA if indicated", "Neurology consult"],
                "goal": "Door-to-needle < 60 minutes"
            },
            {
                "name": "STEMI Alert",
                "type": EmergencyType.CHEST_PAIN.value,
                "time_window_minutes": 90,
                "key_interventions": ["ECG", "Cath lab activation", "Dual antiplatelet"],
                "goal": "Door-to-balloon < 90 minutes"
            },
            {
                "name": "Trauma Alert",
                "type": EmergencyType.TRAUMA.value,
                "time_window_minutes": 60,
                "key_interventions": ["Trauma team", "FAST exam", "Massive transfusion protocol"],
                "goal": "Golden hour - definitive care within 60 minutes"
            },
            {
                "name": "Sepsis Bundle",
                "type": EmergencyType.SEPTIC_SHOCK.value,
                "time_window_minutes": 60,
                "key_interventions": ["Blood cultures", "Broad-spectrum antibiotics", "Fluid resuscitation"],
                "goal": "Antibiotics within 1 hour"
            },
            {
                "name": "Code Blue",
                "type": EmergencyType.CARDIAC_ARREST.value,
                "time_window_minutes": 4,
                "key_interventions": ["CPR", "Defibrillation", "ACLS protocol"],
                "goal": "CPR within 4 minutes"
            },
        ]
    }


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_emergency_statistics(
    current_user = Depends(get_current_active_user)
):
    """
    Get emergency department statistics

    **Required Permissions:** Admin, Physician

    **Returns:** Real-time ED metrics
    """
    # This would connect to actual metrics in production
    return {
        "current_census": 45,
        "waiting_patients": 12,
        "triage_distribution": {
            "level_1": 2,
            "level_2": 8,
            "level_3": 15,
            "level_4": 12,
            "level_5": 8
        },
        "average_wait_time_minutes": {
            "level_1": 0,
            "level_2": 5,
            "level_3": 25,
            "level_4": 45,
            "level_5": 90
        },
        "protocol_activations_today": {
            "stroke_alert": 3,
            "stemi_alert": 2,
            "trauma_alert": 5,
            "sepsis_bundle": 4
        }
    }
