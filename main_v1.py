"""
Healthcare-AI-Quantum-System Main Application

FastAPI application with all agents and endpoints.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logging import get_logger
from core.database import init_databases, close_databases, get_db
from agents.clinical_decision.agent import create_clinical_decision_agent

logger = get_logger()


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown events.
    """
    # STARTUP
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize databases
    await init_databases()

    # Initialize agents
    if settings.enable_clinical_decision_agent:
        app.state.clinical_decision_agent = create_clinical_decision_agent()
        logger.info("Clinical Decision Agent initialized")

    logger.info("Application startup complete")

    yield

    # SHUTDOWN
    logger.info("Shutting down application...")

    # Close databases
    await close_databases()

    logger.info("Application shutdown complete")


# ============================================================================
# CREATE APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="World's First Quantum-Enhanced Multi-Agent Healthcare Management Platform",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in prod
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint

    Returns system status and version.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "agents": {
            "clinical_decision": settings.enable_clinical_decision_agent,
            "resource_optimization": settings.enable_resource_optimization_agent,
            "patient_monitoring": settings.enable_patient_monitoring_agent,
        }
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare-AI-Quantum-System API",
        "version": settings.app_version,
        "docs": "/docs" if not settings.is_production else "disabled",
        "health": "/health"
    }


# ============================================================================
# CLINICAL DECISION ENDPOINTS
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional


class VitalsInput(BaseModel):
    """Vital signs input"""
    heart_rate: Optional[int] = Field(None, description="Heart rate (bpm)")
    blood_pressure_systolic: Optional[int] = Field(None, description="Systolic BP (mmHg)")
    blood_pressure_diastolic: Optional[int] = Field(None, description="Diastolic BP (mmHg)")
    temperature: Optional[float] = Field(None, description="Temperature (Celsius)")
    oxygen_saturation: Optional[float] = Field(None, description="SpO2 (%)")
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate (breaths/min)")


class DiagnosisRequest(BaseModel):
    """Request for clinical diagnosis"""
    patient_id: str = Field(..., description="Patient UUID")
    encounter_id: Optional[str] = Field(None, description="Encounter UUID")
    chief_complaint: str = Field(..., description="Chief complaint", examples=["chest pain"])
    symptoms: List[str] = Field(default_factory=list, description="List of symptoms")
    vitals: Optional[VitalsInput] = Field(None, description="Vital signs")
    medical_history: List[str] = Field(default_factory=list, description="Past medical history")
    current_medications: List[str] = Field(default_factory=list, description="Current medications")
    labs: Optional[Dict[str, float]] = Field(None, description="Lab results")


class DiagnosisResponse(BaseModel):
    """Clinical diagnosis response"""
    decision_id: str
    primary_diagnosis: Optional[Dict[str, Any]]
    differential_diagnoses: List[Dict[str, Any]]
    confidence: float
    recommended_tests: List[Dict[str, Any]]
    treatment_suggestions: List[Dict[str, Any]]
    drug_warnings: List[Dict[str, str]]
    requires_human_review: bool
    explanation: Optional[str]
    urgent_flags: List[str]


@app.post(
    "/api/v1/clinical-decision/diagnose",
    response_model=DiagnosisResponse,
    tags=["Clinical Decision"],
    summary="Get AI-assisted diagnosis",
    description="Submit patient data for clinical decision support and differential diagnosis"
)
async def diagnose_patient(
    request: DiagnosisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI-Assisted Clinical Diagnosis

    Analyzes patient presentation and provides:
    - Differential diagnosis with probabilities
    - Recommended diagnostic tests
    - Treatment suggestions
    - Drug interaction warnings

    **Requirements:**
    - Patient ID (UUID)
    - Chief complaint

    **Optional:**
    - Vital signs, symptoms, medical history, labs

    **Returns:**
    - Structured diagnosis with confidence scores
    - Evidence-based recommendations
    - Critical findings flagged
    """
    # Check if agent is enabled
    if not settings.enable_clinical_decision_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clinical Decision Agent is not enabled"
        )

    # Get agent from app state
    agent = app.state.clinical_decision_agent

    # Prepare input data
    input_data = {
        "patient_id": request.patient_id,
        "encounter_id": request.encounter_id,
        "chief_complaint": request.chief_complaint,
        "symptoms": request.symptoms,
        "vitals": request.vitals.dict() if request.vitals else {},
        "medical_history": request.medical_history,
        "current_medications": request.current_medications,
        "labs": request.labs or {}
    }

    try:
        # Process with agent
        result = await agent.process(input_data, db)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent processing failed: {', '.join(result.errors)}"
            )

        # Extract output
        clinical_output = result.details["clinical_output"]
        urgent_flags = result.details["urgent_flags"]

        # Build response
        response = DiagnosisResponse(
            decision_id=str(result.result_id),
            primary_diagnosis=clinical_output["primary_diagnosis"],
            differential_diagnoses=clinical_output["differential_diagnoses"],
            confidence=clinical_output["confidence"],
            recommended_tests=clinical_output["recommended_tests"],
            treatment_suggestions=clinical_output["treatment_suggestions"],
            drug_warnings=clinical_output["drug_warnings"],
            requires_human_review=clinical_output["requires_human_review"],
            explanation=clinical_output["explanation"],
            urgent_flags=urgent_flags
        )

        return response

    except Exception as e:
        logger.error(f"Diagnosis request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get(
    "/api/v1/clinical-decision/metrics",
    tags=["Clinical Decision"],
    summary="Get agent metrics"
)
async def get_clinical_decision_metrics():
    """Get Clinical Decision Agent performance metrics"""
    if not settings.enable_clinical_decision_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clinical Decision Agent is not enabled"
        )

    agent = app.state.clinical_decision_agent
    return agent.get_metrics()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_type=type(exc).__name__)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=1 if settings.api_reload else settings.api_workers,
        log_level=settings.log_level.lower()
    )
