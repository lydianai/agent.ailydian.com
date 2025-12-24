"""
Healthcare-AI-Quantum-System Main Application - FULL VERSION

Complete production-ready API with all agents, authentication, and monitoring.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any, List
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.config import settings
from core.logging import get_logger
from core.database import init_databases, close_databases, get_db
from core.security import (
    User, get_current_user, create_access_token, authenticate_user,
    require_physician, require_nurse
)

# Import all agents
from agents.clinical_decision.agent import create_clinical_decision_agent
from agents.resource_optimization.agent import create_resource_optimization_agent
from agents.patient_monitoring.agent import create_patient_monitoring_agent

logger = get_logger()


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""

    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize databases
    await init_databases()

    # Initialize agents
    if settings.enable_clinical_decision_agent:
        app.state.clinical_decision_agent = create_clinical_decision_agent()
        logger.info("✅ Clinical Decision Agent initialized")

    if settings.enable_resource_optimization_agent:
        app.state.resource_optimization_agent = create_resource_optimization_agent()
        logger.info("✅ Resource Optimization Agent initialized")

    if settings.enable_patient_monitoring_agent:
        app.state.patient_monitoring_agent = create_patient_monitoring_agent()
        logger.info("✅ Patient Monitoring Agent initialized")

    logger.info("🎉 Application startup complete")

    yield

    # SHUTDOWN
    logger.info("Shutting down application...")
    await close_databases()
    logger.info("Application shutdown complete")


# ============================================================================
# CREATE APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="World's First Quantum-Enhanced Multi-Agent Healthcare Management Platform - FULL VERSION",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
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
# AUTHENTICATION ENDPOINTS
# ============================================================================

class Token(BaseModel):
    """Access token response"""
    access_token: str
    token_type: str


@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login

    Test credentials (development only):
    - Username: dr.smith
    - Password: password123
    """

    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.user_id,
            "username": user.username,
            "roles": user.roles
        },
        expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {user.username}")

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "agents": {
            "clinical_decision": settings.enable_clinical_decision_agent,
            "resource_optimization": settings.enable_resource_optimization_agent,
            "patient_monitoring": settings.enable_patient_monitoring_agent,
        },
        "features": {
            "quantum_computing": settings.enable_quantum_optimization,
            "authentication": True,
            "fhir_integration": True,
            "real_time_monitoring": True
        }
    }


# ============================================================================
# CLINICAL DECISION ENDPOINTS
# ============================================================================

from typing import Optional


class VitalsInput(BaseModel):
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    respiratory_rate: Optional[int] = None


class DiagnosisRequest(BaseModel):
    patient_id: str
    encounter_id: Optional[str] = None
    chief_complaint: str
    symptoms: List[str] = Field(default_factory=list)
    vitals: Optional[VitalsInput] = None
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    labs: Optional[Dict[str, float]] = None


@app.post("/api/v1/clinical-decision/diagnose", tags=["Clinical Decision"])
async def diagnose_patient(
    request: DiagnosisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_physician)  # Requires physician role
):
    """AI-Assisted Clinical Diagnosis (Requires Physician Role)"""

    if not settings.enable_clinical_decision_agent:
        raise HTTPException(503, "Clinical Decision Agent not enabled")

    agent = app.state.clinical_decision_agent

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

    result = await agent.process(input_data, db)

    if not result.success:
        raise HTTPException(500, f"Agent failed: {', '.join(result.errors)}")

    return result.details["clinical_output"]


# ============================================================================
# RESOURCE OPTIMIZATION ENDPOINTS
# ============================================================================

class SurgeryInput(BaseModel):
    surgery_id: str
    patient_id: str
    procedure_name: str
    duration_minutes: int
    priority: int = Field(ge=1, le=3, description="1=emergency, 2=urgent, 3=elective")
    surgeon_id: str
    required_equipment: List[str] = Field(default_factory=list)
    preferred_or: Optional[str] = None


class ORInput(BaseModel):
    or_id: str
    name: str
    equipment: List[str] = Field(default_factory=list)
    room_type: str = "general"


class ORScheduleRequest(BaseModel):
    date: str = Field(description="Date in ISO format (YYYY-MM-DD)")
    surgeries: List[SurgeryInput]
    operating_rooms: List[ORInput]


@app.post("/api/v1/resource-optimization/or-schedule", tags=["Resource Optimization"])
async def optimize_or_schedule(
    request: ORScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_nurse)  # Nurses can schedule
):
    """
    Optimize Operating Room Schedule (Quantum-Enhanced)

    Uses QAOA on IBM Quantum hardware when available.
    """

    if not settings.enable_resource_optimization_agent:
        raise HTTPException(503, "Resource Optimization Agent not enabled")

    agent = app.state.resource_optimization_agent

    input_data = {
        "optimization_type": "or_scheduling",
        "date": request.date,
        "surgeries": [s.dict() for s in request.surgeries],
        "operating_rooms": [o.dict() for o in request.operating_rooms]
    }

    result = await agent.process(input_data, db)

    if not result.success:
        raise HTTPException(500, f"Optimization failed: {', '.join(result.errors)}")

    return result.details["optimization_result"]


# ============================================================================
# PATIENT MONITORING ENDPOINTS
# ============================================================================

class PatientMonitorRequest(BaseModel):
    patient_id: str
    vital_signs: VitalsInput


@app.post("/api/v1/patient-monitoring/assess", tags=["Patient Monitoring"])
async def assess_patient_status(
    request: PatientMonitorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_nurse)
):
    """
    Assess Patient Status (Real-time Monitoring)

    Includes:
    - NEWS2 early warning score
    - Sepsis risk assessment
    - Alert generation
    """

    if not settings.enable_patient_monitoring_agent:
        raise HTTPException(503, "Patient Monitoring Agent not enabled")

    agent = app.state.patient_monitoring_agent

    input_data = {
        "patient_id": request.patient_id,
        "vital_signs": request.vital_signs.dict()
    }

    result = await agent.process(input_data, db)

    if not result.success:
        raise HTTPException(500, f"Assessment failed: {', '.join(result.errors)}")

    return result.details


# ============================================================================
# AGENT METRICS
# ============================================================================

@app.get("/api/v1/metrics/agents", tags=["Metrics"])
async def get_all_agent_metrics(current_user: User = Depends(get_current_user)):
    """Get performance metrics for all agents"""

    metrics = {}

    if settings.enable_clinical_decision_agent:
        metrics["clinical_decision"] = app.state.clinical_decision_agent.get_metrics()

    if settings.enable_resource_optimization_agent:
        metrics["resource_optimization"] = app.state.resource_optimization_agent.get_metrics()

    if settings.enable_patient_monitoring_agent:
        metrics["patient_monitoring"] = app.state.patient_monitoring_agent.get_metrics()

    return metrics


# ============================================================================
# SYSTEM INFO
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """API information"""
    return {
        "message": "Healthcare-AI-Quantum-System API - FULL VERSION",
        "version": settings.app_version,
        "docs": "/docs" if not settings.is_production else "disabled",
        "authentication": "Bearer token required for protected endpoints",
        "agents": {
            "clinical_decision": settings.enable_clinical_decision_agent,
            "resource_optimization": settings.enable_resource_optimization_agent,
            "patient_monitoring": settings.enable_patient_monitoring_agent,
        }
    }


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
