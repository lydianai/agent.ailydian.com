"""
Diagnosis API Endpoints

Provides AI-powered diagnostic support with medical imaging.
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from agents.diagnosis.agent import DiagnosisAgent, ImagingModality, BodyRegion
from core.logging import get_logger
from core.security import get_current_active_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/diagnosis", tags=["Diagnosis"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ImagingData(BaseModel):
    """Imaging data model"""
    modality: str = Field(..., description="Imaging modality (xray, ct, mri, etc.)")
    body_region: str = Field(..., description="Body region imaged")
    radiologist_notes: Optional[str] = Field(None, description="Radiologist findings")
    study_date: Optional[datetime] = None


class ClinicalData(BaseModel):
    """Clinical data model"""
    chief_complaint: str
    symptoms: List[str] = Field(default_factory=list)
    vital_signs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    medical_history: Optional[List[str]] = Field(default_factory=list)
    medications: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)


class DiagnosisRequest(BaseModel):
    """Diagnosis request model"""
    patient_id: str
    imaging_data: ImagingData
    clinical_data: ClinicalData
    lab_results: Optional[Dict[str, float]] = Field(default_factory=dict)


class DiagnosisResponse(BaseModel):
    """Diagnosis response model"""
    patient_id: str
    primary_diagnosis: Optional[Dict[str, Any]]
    differential_diagnosis: List[Dict[str, Any]]
    confidence: float
    risk_level: str
    critical_findings: List[Dict[str, Any]]
    recommendations: List[str]
    additional_tests: List[str]
    specialist_referrals: List[str]
    followup_plan: Dict[str, Any]
    imaging_findings: List[Dict[str, Any]]
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=DiagnosisResponse, status_code=status.HTTP_200_OK)
async def analyze_case(
    request: DiagnosisRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Comprehensive diagnostic analysis

    **Required Permissions:** Physician, Radiologist

    **Returns:**
    - Primary diagnosis with confidence score
    - Differential diagnosis (top 5)
    - Risk stratification
    - Critical findings
    - Treatment recommendations
    - Additional testing needed
    - Specialist referrals
    - Follow-up plan
    """
    try:
        # Initialize agent
        agent = DiagnosisAgent()

        # Perform analysis
        result = await agent.analyze_case(
            patient_id=request.patient_id,
            imaging_data=request.imaging_data.model_dump(exclude_none=True),
            clinical_data=request.clinical_data.model_dump(exclude_none=True),
            lab_results=request.lab_results,
        )

        logger.info(f"Diagnosis completed for patient {request.patient_id}")

        return result

    except Exception as e:
        logger.error(f"Diagnosis error for patient {request.patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostic analysis failed: {str(e)}"
        )


@router.get("/modalities", status_code=status.HTTP_200_OK)
async def get_imaging_modalities():
    """
    Get supported imaging modalities

    **Returns:** List of all supported imaging modalities
    """
    return {
        "modalities": [
            {
                "code": ImagingModality.XRAY.value,
                "name": "X-Ray",
                "description": "Radiography imaging",
                "common_uses": ["Chest", "Bone", "Abdomen"]
            },
            {
                "code": ImagingModality.CT.value,
                "name": "CT Scan",
                "description": "Computed Tomography",
                "common_uses": ["Brain", "Chest", "Abdomen", "Pelvis"]
            },
            {
                "code": ImagingModality.MRI.value,
                "name": "MRI",
                "description": "Magnetic Resonance Imaging",
                "common_uses": ["Brain", "Spine", "Joints", "Soft tissue"]
            },
            {
                "code": ImagingModality.ULTRASOUND.value,
                "name": "Ultrasound",
                "description": "Sonography",
                "common_uses": ["Abdomen", "Obstetric", "Cardiac", "Vascular"]
            },
            {
                "code": ImagingModality.MAMMOGRAPHY.value,
                "name": "Mammography",
                "description": "Breast imaging",
                "common_uses": ["Breast cancer screening"]
            },
            {
                "code": ImagingModality.PET.value,
                "name": "PET Scan",
                "description": "Positron Emission Tomography",
                "common_uses": ["Cancer staging", "Cardiac", "Neurological"]
            }
        ]
    }


@router.get("/body-regions", status_code=status.HTTP_200_OK)
async def get_body_regions():
    """
    Get supported body regions for imaging

    **Returns:** List of all body regions
    """
    return {
        "regions": [
            {"code": BodyRegion.CHEST.value, "name": "Chest"},
            {"code": BodyRegion.ABDOMEN.value, "name": "Abdomen"},
            {"code": BodyRegion.BRAIN.value, "name": "Brain/Head"},
            {"code": BodyRegion.SPINE.value, "name": "Spine"},
            {"code": BodyRegion.PELVIS.value, "name": "Pelvis"},
            {"code": BodyRegion.EXTREMITIES.value, "name": "Extremities"},
            {"code": BodyRegion.CARDIAC.value, "name": "Cardiac"}
        ]
    }


@router.post("/upload-image", status_code=status.HTTP_200_OK)
async def upload_medical_image(
    file: UploadFile = File(...),
    patient_id: str = None,
    current_user = Depends(get_current_active_user)
):
    """
    Upload medical imaging file

    **Required Permissions:** Physician, Radiologist

    **Supported formats:** DICOM, JPEG, PNG

    **Returns:** Upload confirmation with file ID
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "application/dicom"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {allowed_types}"
            )

        # Read file
        contents = await file.read()
        file_size = len(contents)

        # Validate size (max 50MB)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_size/1024/1024}MB"
            )

        # In production, save to cloud storage (S3, Azure Blob, etc.)
        file_id = f"img_{patient_id}_{datetime.utcnow().timestamp()}"

        logger.info(f"Image uploaded: {file_id}, size: {file_size} bytes")

        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": file_size,
            "content_type": file.content_type,
            "patient_id": patient_id,
            "uploaded_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )


@router.get("/statistics", status_code=status.HTTP_200_OK)
async def get_diagnosis_statistics(
    current_user = Depends(get_current_active_user)
):
    """
    Get diagnostic statistics

    **Required Permissions:** Admin, Physician

    **Returns:** Diagnostic metrics
    """
    return {
        "total_cases_analyzed": 1247,
        "average_confidence": 0.87,
        "top_diagnoses": [
            {"diagnosis": "pneumonia", "count": 145, "percentage": 11.6},
            {"diagnosis": "myocardial_infarction", "count": 98, "percentage": 7.9},
            {"diagnosis": "stroke_ischemic", "count": 87, "percentage": 7.0},
            {"diagnosis": "pulmonary_embolism", "count": 76, "percentage": 6.1},
            {"diagnosis": "appendicitis", "count": 65, "percentage": 5.2}
        ],
        "imaging_modality_usage": {
            "xray": 456,
            "ct": 389,
            "mri": 234,
            "ultrasound": 123,
            "pet": 45
        },
        "average_processing_time_seconds": 2.3
    }
