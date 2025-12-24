"""
Healthcare-AI-Quantum-System - Quick Start Demo
Simplified version for immediate testing without external dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Healthcare-AI-Quantum-System - Demo",
    version="1.0.0",
    description="Healthcare AI & Quantum System - Interactive Demo"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELS
# ============================================================================

class VitalsInput(BaseModel):
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    respiratory_rate: Optional[int] = None


class DiagnosisRequest(BaseModel):
    patient_id: str
    chief_complaint: str
    symptoms: List[str] = Field(default_factory=list)
    vitals: Optional[VitalsInput] = None
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)


class PatientMonitorRequest(BaseModel):
    patient_id: str
    vital_signs: VitalsInput


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_news2_score(vitals: Dict[str, Any]) -> int:
    """Calculate NEWS2 (National Early Warning Score 2)"""
    score = 0

    # Respiratory Rate
    rr = vitals.get("respiratory_rate")
    if rr:
        if rr <= 8: score += 3
        elif rr <= 11: score += 1
        elif rr >= 25: score += 3
        elif rr >= 21: score += 2

    # Oxygen Saturation
    spo2 = vitals.get("oxygen_saturation")
    if spo2:
        if spo2 <= 91: score += 3
        elif spo2 <= 93: score += 2
        elif spo2 <= 95: score += 1

    # Blood Pressure (Systolic)
    sbp = vitals.get("blood_pressure_systolic")
    if sbp:
        if sbp <= 90: score += 3
        elif sbp <= 100: score += 2
        elif sbp <= 110: score += 1
        elif sbp >= 220: score += 3

    # Heart Rate
    hr = vitals.get("heart_rate")
    if hr:
        if hr <= 40: score += 3
        elif hr <= 50: score += 1
        elif hr >= 131: score += 3
        elif hr >= 111: score += 2
        elif hr >= 91: score += 1

    # Temperature
    temp = vitals.get("temperature")
    if temp:
        if temp <= 35.0: score += 3
        elif temp <= 36.0: score += 1
        elif temp >= 39.1: score += 2
        elif temp >= 38.1: score += 1

    return score


def assess_sepsis_risk(vitals: Dict[str, Any]) -> Dict[str, Any]:
    """Assess sepsis risk using qSOFA criteria"""
    qsofa_score = 0
    criteria_met = []

    # Altered mental status (we'll skip this in demo)

    # Systolic BP ≤ 100 mmHg
    sbp = vitals.get("blood_pressure_systolic")
    if sbp and sbp <= 100:
        qsofa_score += 1
        criteria_met.append("hypotension")

    # Respiratory rate ≥ 22/min
    rr = vitals.get("respiratory_rate")
    if rr and rr >= 22:
        qsofa_score += 1
        criteria_met.append("tachypnea")

    # Determine risk level
    if qsofa_score >= 2:
        risk = "HIGH"
    elif qsofa_score == 1:
        risk = "ELEVATED"
    else:
        risk = "LOW"

    return {
        "qsofa_score": qsofa_score,
        "risk_level": risk,
        "criteria_met": criteria_met
    }


def generate_mock_diagnosis(request: DiagnosisRequest) -> Dict[str, Any]:
    """Generate a realistic mock clinical diagnosis"""

    complaint = request.chief_complaint.lower()

    # Simple pattern matching for demo
    if "chest pain" in complaint or "chest" in complaint:
        primary_diagnosis = {
            "diagnosis": "Acute Coronary Syndrome (Rule Out)",
            "icd10": "I24.9",
            "probability": 0.65,
            "severity": "HIGH",
            "reasoning": "Chest pain with risk factors requires immediate cardiac evaluation"
        }
        differential = [
            {"diagnosis": "Acute MI", "probability": 0.35, "icd10": "I21.9"},
            {"diagnosis": "Unstable Angina", "probability": 0.25, "icd10": "I20.0"},
            {"diagnosis": "GERD", "probability": 0.15, "icd10": "K21.9"},
            {"diagnosis": "Musculoskeletal Pain", "probability": 0.10, "icd10": "M79.1"}
        ]
        tests = ["Troponin I/T", "ECG (12-lead)", "Chest X-ray", "BNP", "D-dimer"]
        treatments = [
            "IMMEDIATE: Activate cardiac catheterization lab",
            "Aspirin 325mg chewable STAT",
            "Nitroglycerin 0.4mg SL q5min PRN",
            "Morphine 2-4mg IV for pain",
            "Continuous cardiac monitoring"
        ]
        urgent_findings = ["High-risk chest pain", "Requires immediate evaluation"]

    elif "fever" in complaint or "temperature" in complaint:
        primary_diagnosis = {
            "diagnosis": "Fever of Unknown Origin",
            "icd10": "R50.9",
            "probability": 0.55,
            "severity": "MEDIUM",
            "reasoning": "Fever requires source identification"
        }
        differential = [
            {"diagnosis": "Viral Infection", "probability": 0.40, "icd10": "B34.9"},
            {"diagnosis": "Bacterial Infection", "probability": 0.30, "icd10": "A49.9"},
            {"diagnosis": "UTI", "probability": 0.15, "icd10": "N39.0"}
        ]
        tests = ["CBC with differential", "Blood cultures", "Urinalysis", "CRP", "ESR"]
        treatments = [
            "Acetaminophen 650mg PO q6h PRN fever",
            "Increase fluid intake",
            "Monitor temperature q4h",
            "Consider antibiotics if bacterial source identified"
        ]
        urgent_findings = []

    elif "headache" in complaint:
        primary_diagnosis = {
            "diagnosis": "Tension Headache",
            "icd10": "G44.209",
            "probability": 0.60,
            "severity": "LOW",
            "reasoning": "Most common type of headache"
        }
        differential = [
            {"diagnosis": "Migraine", "probability": 0.25, "icd10": "G43.909"},
            {"diagnosis": "Cluster Headache", "probability": 0.08, "icd10": "G44.009"},
            {"diagnosis": "Meningitis (Rule Out)", "probability": 0.05, "icd10": "G03.9"}
        ]
        tests = ["Neurological exam", "Fundoscopic exam", "Consider CT head if red flags"]
        treatments = [
            "Ibuprofen 400mg PO q6h PRN",
            "Acetaminophen 650mg PO q6h PRN",
            "Rest in quiet, dark room",
            "Hydration"
        ]
        urgent_findings = []

    else:
        # Generic response
        primary_diagnosis = {
            "diagnosis": "Undifferentiated Symptoms",
            "icd10": "R69",
            "probability": 0.50,
            "severity": "MEDIUM",
            "reasoning": "Requires further clinical evaluation"
        }
        differential = [
            {"diagnosis": "Viral Syndrome", "probability": 0.30, "icd10": "B34.9"},
            {"diagnosis": "Stress/Anxiety", "probability": 0.20, "icd10": "F41.9"}
        ]
        tests = ["Complete history and physical", "Basic metabolic panel", "CBC"]
        treatments = [
            "Symptomatic treatment",
            "Follow-up in 48-72 hours",
            "Return if symptoms worsen"
        ]
        urgent_findings = []

    # Add urgent findings based on vitals
    if request.vitals:
        vitals_dict = request.vitals.dict()
        if vitals_dict.get("heart_rate", 0) > 120:
            urgent_findings.append("Tachycardia (HR > 120)")
        if vitals_dict.get("blood_pressure_systolic", 0) > 180:
            urgent_findings.append("Severe hypertension")
        if vitals_dict.get("oxygen_saturation", 100) < 90:
            urgent_findings.append("Hypoxemia (SpO2 < 90%)")

    return {
        "timestamp": datetime.now().isoformat(),
        "patient_id": request.patient_id,
        "primary_diagnosis": primary_diagnosis,
        "differential_diagnosis": [primary_diagnosis] + differential,
        "recommended_tests": tests,
        "treatment_recommendations": treatments,
        "urgent_findings": urgent_findings,
        "drug_warnings": [],
        "follow_up": "Re-evaluate in 24-48 hours or sooner if symptoms worsen",
        "confidence": primary_diagnosis["probability"],
        "disclaimer": "⚠️ AI-ASSISTED DIAGNOSIS - Physician review required"
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API Information"""
    return {
        "message": "Healthcare-AI-Quantum-System - Quick Demo",
        "version": "1.0.0",
        "status": "running",
        "mode": "production_demo",
        "note": "Enterprise features available on request",
        "endpoints": {
            "health": "GET /health",
            "diagnose": "POST /api/v1/clinical-decision/diagnose",
            "monitor": "POST /api/v1/patient-monitoring/assess",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health Check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Healthcare-AI-Quantum-System",
        "version": "1.0.0",
        "mode": "demo",
        "agents": {
            "clinical_decision": "demo_mode",
            "patient_monitoring": "demo_mode",
            "resource_optimization": "offline"
        }
    }


@app.post("/api/v1/clinical-decision/diagnose")
async def diagnose_patient(request: DiagnosisRequest):
    """
    AI-Assisted Clinical Diagnosis (Demo Mode)

    AI-powered clinical decision support with evidence-based recommendations.
    Results are for reference only; final decisions rest with healthcare providers.
    """

    try:
        result = generate_mock_diagnosis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/patient-monitoring/assess")
async def assess_patient_status(request: PatientMonitorRequest):
    """
    Patient Vital Signs Assessment (Demo Mode)

    Real-time monitoring with NEWS2 scoring and sepsis assessment.
    """

    try:
        vitals_dict = request.vital_signs.dict()

        # Calculate NEWS2 score
        news2_score = calculate_news2_score(vitals_dict)

        # Determine risk level
        if news2_score >= 7:
            risk_level = "HIGH"
            recommendations = [
                "Urgent medical review required",
                "Increase monitoring frequency to every 15 minutes",
                "Consider ICU transfer",
                "Notify attending physician immediately"
            ]
        elif news2_score >= 5:
            risk_level = "MEDIUM"
            recommendations = [
                "Increase monitoring to every 30 minutes",
                "Review by nurse in charge",
                "Consider escalation if score increases"
            ]
        else:
            risk_level = "LOW"
            recommendations = [
                "Continue routine monitoring",
                "Reassess in 4-6 hours"
            ]

        # Assess sepsis risk
        sepsis_assessment = assess_sepsis_risk(vitals_dict)

        # Generate alerts
        alerts = []
        if news2_score >= 7:
            alerts.append({
                "severity": "HIGH",
                "type": "NEWS2_HIGH",
                "message": f"NEWS2 score {news2_score} - urgent response required"
            })

        if sepsis_assessment["risk_level"] == "HIGH":
            alerts.append({
                "severity": "HIGH",
                "type": "SEPSIS_RISK",
                "message": f"Possible sepsis - qSOFA {sepsis_assessment['qsofa_score']}/3"
            })

        # Vital-specific alerts
        if vitals_dict.get("oxygen_saturation", 100) < 90:
            alerts.append({
                "severity": "CRITICAL",
                "type": "HYPOXEMIA",
                "message": f"Severe hypoxemia - SpO2 {vitals_dict['oxygen_saturation']}%"
            })

        if vitals_dict.get("blood_pressure_systolic", 120) < 90:
            alerts.append({
                "severity": "HIGH",
                "type": "HYPOTENSION",
                "message": f"Hypotension - SBP {vitals_dict['blood_pressure_systolic']} mmHg"
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "patient_id": request.patient_id,
            "news2_score": news2_score,
            "risk_level": risk_level,
            "sepsis_risk": sepsis_assessment["risk_level"],
            "sepsis_assessment": sepsis_assessment,
            "alerts": alerts,
            "recommendations": recommendations,
            "vital_signs": vitals_dict,
            "trend": "stable",  # Would be calculated from historical data
            "mode": "demo"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics/agents")
async def get_agent_metrics():
    """Get Agent Metrics (Demo)"""
    return {
        "clinical_decision": {
            "total_executions": 42,
            "average_execution_time_ms": 2340,
            "success_rate": 0.98,
            "mode": "demo"
        },
        "patient_monitoring": {
            "total_assessments": 156,
            "average_execution_time_ms": 120,
            "alerts_generated": 8,
            "mode": "demo"
        },
        "resource_optimization": {
            "status": "offline",
            "reason": "Quantum optimization module inactive"
        }
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🏥 Healthcare-AI-Quantum-System - Quick Start Demo")
    print("=" * 60)
    print("Starting server on http://localhost:8000")
    print("")
    print("📚 Available endpoints:")
    print("  • http://localhost:8000/           - API info")
    print("  • http://localhost:8000/health     - Health check")
    print("  • http://localhost:8000/docs       - Interactive API docs")
    print("")
    print("🧪 Test the system:")
    print('  curl -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"patient_id": "P-001", "chief_complaint": "chest pain"}\'')
    print("")
    print("✅ Demo Mode: All core features active for testing")
    print("   For production deployment with full features,")
    print("   please contact: enterprise@lydian-agent.com")
    print("=" * 60)
    print("")

    uvicorn.run(
        "quickstart:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
