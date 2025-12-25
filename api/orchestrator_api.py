"""
Orchestrator API Integration

API endpoints for Task Agent Orchestrator system.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/orchestrator", tags=["Orchestrator"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TaskSubmitRequest(BaseModel):
    """Task submission request"""
    task_type: str
    priority: int = 5  # 1-5, 1=critical
    required_capabilities: List[str] = []
    data: Dict[str, Any]
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    task_type: str
    status: str
    assigned_agent_id: Optional[str] = None
    created_at: str
    result: Optional[Dict[str, Any]] = None


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    name: str
    status: str
    category: str
    tasks_completed: int
    success_rate: float
    active_tasks: int


# ============================================================================
# MOCK DATA (Production would use actual orchestrator)
# ============================================================================

MOCK_ORCHESTRATOR_STATUS = {
    "status": "operational",
    "started_at": datetime.utcnow().isoformat(),
    "uptime_seconds": 3600.5,
    "agent_stats": {
        "total_agents": 10,
        "active": 9,
        "idle": 1,
        "busy": 5,
        "error": 0,
        "offline": 0,
        "total_tasks_completed": 1847,
        "total_tasks_failed": 23,
        "avg_success_rate": 98.76,
    },
    "routing_stats": {
        "total_tasks": 1870,
        "pending": 5,
        "assigned": 12,
        "in_progress": 8,
        "completed": 1847,
        "failed": 23,
        "queue_size": 5,
    },
    "message_bus": {
        "topics": [
            "task.submitted",
            "task.completed",
            "task.failed",
            "agent.registered",
            "agent.failed"
        ],
        "message_count": 847,
    }
}

MOCK_AGENTS = [
    {
        "agent_id": "quantum-optimizer",
        "name": "Quantum Resource Optimizer",
        "status": "active",
        "category": "quantum",
        "tasks_completed": 156,
        "tasks_failed": 2,
        "success_rate": 98.7,
        "active_tasks": 1,
        "capabilities": ["or_scheduling", "staff_rostering", "bed_allocation", "quantum_optimization"],
        "metrics": {
            "or_utilization_improvement": 32,
            "time_saved_minutes": 18,
            "avg_response_time_ms": 1200,
        }
    },
    {
        "agent_id": "sepsis-prediction",
        "name": "Sepsis Prediction & Intervention",
        "status": "active",
        "category": "emergency",
        "tasks_completed": 287,
        "tasks_failed": 4,
        "success_rate": 98.6,
        "active_tasks": 2,
        "capabilities": ["vital_monitoring", "sepsis_detection", "early_warning", "protocol_activation"],
        "metrics": {
            "early_detection_hours": 2.4,
            "accuracy_percent": 94.2,
            "alerts_per_day": 8,
        }
    },
    {
        "agent_id": "surgical-safety",
        "name": "Surgical Safety Checklist",
        "status": "active",
        "category": "clinical",
        "tasks_completed": 245,
        "tasks_failed": 0,
        "success_rate": 100.0,
        "active_tasks": 1,
        "capabilities": ["checklist_verification", "instrument_counting", "patient_verification"],
        "metrics": {
            "compliance_percent": 100,
            "wrong_site_surgeries": 0,
            "checks_per_day": 24,
        }
    },
    {
        "agent_id": "radiology-reporting",
        "name": "Radiology Auto-Reporting",
        "status": "busy",
        "category": "clinical",
        "tasks_completed": 412,
        "tasks_failed": 8,
        "success_rate": 98.1,
        "active_tasks": 3,
        "capabilities": ["image_analysis", "report_generation", "critical_findings"],
        "metrics": {
            "accuracy_percent": 95.8,
            "time_saved_percent": 52,
            "reports_per_day": 67,
        }
    },
    {
        "agent_id": "medication-reconciliation",
        "name": "Medication Reconciliation",
        "status": "active",
        "category": "clinical",
        "tasks_completed": 324,
        "tasks_failed": 5,
        "success_rate": 98.5,
        "active_tasks": 2,
        "capabilities": ["drug_interaction", "dose_checking", "medication_history"],
        "metrics": {
            "error_reduction_percent": 72,
            "checks_per_day": 45,
            "adverse_events_prevented": 8,
        }
    },
    {
        "agent_id": "clinical-trial-matching",
        "name": "Clinical Trial Matching",
        "status": "idle",
        "category": "research",
        "tasks_completed": 89,
        "tasks_failed": 2,
        "success_rate": 97.8,
        "active_tasks": 0,
        "capabilities": ["eligibility_screening", "trial_matching", "patient_outreach"],
        "metrics": {
            "matches_found": 12,
            "patients_enrolled": 8,
            "active_trials": 3,
        }
    },
    {
        "agent_id": "readmission-prevention",
        "name": "Predictive Readmission Prevention",
        "status": "active",
        "category": "operational",
        "tasks_completed": 178,
        "tasks_failed": 1,
        "success_rate": 99.4,
        "active_tasks": 1,
        "capabilities": ["risk_scoring", "followup_scheduling", "patient_monitoring"],
        "metrics": {
            "readmission_reduction_percent": 27,
            "high_risk_patients": 18,
            "cost_saved_millions": 1.8,
        }
    },
    {
        "agent_id": "outbreak-detector",
        "name": "Infectious Disease Outbreak Detector",
        "status": "active",
        "category": "emergency",
        "tasks_completed": 134,
        "tasks_failed": 0,
        "success_rate": 100.0,
        "active_tasks": 1,
        "capabilities": ["infection_surveillance", "outbreak_detection", "contact_tracing"],
        "metrics": {
            "hai_reduction_percent": 42,
            "detection_time_hours": 36,
            "active_outbreaks": 0,
        }
    },
    {
        "agent_id": "mental-health-crisis",
        "name": "Mental Health Crisis Predictor",
        "status": "active",
        "category": "clinical",
        "tasks_completed": 98,
        "tasks_failed": 1,
        "success_rate": 99.0,
        "active_tasks": 1,
        "capabilities": ["risk_assessment", "crisis_detection", "suicide_prevention"],
        "metrics": {
            "prevention_rate_percent": 52,
            "response_time_minutes": 28,
            "alerts_per_week": 12,
        }
    },
    {
        "agent_id": "genomic-therapy",
        "name": "Genomic Therapy Recommender",
        "status": "active",
        "category": "research",
        "tasks_completed": 67,
        "tasks_failed": 0,
        "success_rate": 100.0,
        "active_tasks": 1,
        "capabilities": ["genomic_analysis", "therapy_matching", "precision_medicine"],
        "metrics": {
            "response_improvement_percent": 32,
            "survival_increase_months": 14,
            "active_patients": 6,
        }
    },
]

MOCK_ACTIVITY = [
    {
        "agent_id": "quantum-optimizer",
        "agent_name": "Quantum Resource Optimizer",
        "task": "Optimized OR schedule for tomorrow: 18 surgeries allocated with 98% efficiency",
        "timestamp": datetime.utcnow().isoformat(),
        "icon": "⚛️"
    },
    {
        "agent_id": "sepsis-prediction",
        "agent_name": "Sepsis Prediction Agent",
        "task": "Alert: Patient P-4521 showing early sepsis indicators (SOFA score: 4). Physician notified.",
        "timestamp": datetime.utcnow().isoformat(),
        "icon": "🚨"
    },
    {
        "agent_id": "medication-reconciliation",
        "agent_name": "Medication Reconciliation",
        "task": "Prevented adverse drug interaction: Warfarin + Aspirin flagged for Patient P-3847",
        "timestamp": datetime.utcnow().isoformat(),
        "icon": "💊"
    },
]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_orchestrator_status():
    """Get orchestrator status and metrics"""
    return MOCK_ORCHESTRATOR_STATUS


@router.get("/agents")
async def get_all_agents(active_only: bool = False):
    """Get all registered agents"""
    agents = MOCK_AGENTS

    if active_only:
        agents = [a for a in agents if a["status"] in ["active", "busy", "idle"]]

    return {"agents": agents, "total": len(agents)}


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get specific agent details"""
    agent = next((a for a in MOCK_AGENTS if a["agent_id"] == agent_id), None)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.get("/activity")
async def get_agent_activity(limit: int = 50):
    """Get recent agent activity"""
    return {"activities": MOCK_ACTIVITY[:limit]}


@router.post("/tasks")
async def submit_task(request: TaskSubmitRequest):
    """Submit a new task to the orchestrator"""
    import uuid

    task_id = f"task_{uuid.uuid4().hex[:8]}"

    return {
        "task_id": task_id,
        "task_type": request.task_type,
        "status": "pending",
        "priority": request.priority,
        "created_at": datetime.utcnow().isoformat(),
        "message": "Task submitted successfully"
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    # Mock task status
    return {
        "task_id": task_id,
        "task_type": "sepsis_screening",
        "status": "completed",
        "assigned_agent_id": "sepsis-prediction",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "result": {
            "patient_id": "P-1234",
            "risk_level": "low",
            "sofa_score": 1,
            "recommendations": ["Continue monitoring", "Reassess in 4 hours"]
        }
    }


@router.get("/health")
async def orchestrator_health():
    """Orchestrator health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "orchestrator": "running",
        "agents_online": 9,
        "tasks_in_queue": 5
    }
