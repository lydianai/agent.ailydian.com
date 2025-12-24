"""
Patient Monitoring Agent

Real-time patient vital signs monitoring with ML-based early warning system.
"""

from typing import Dict, Any
from datetime import datetime

from core.agents.base_agent import (
    BaseHealthcareAgent, Observation, Decision, ActionResult
)
from core.config import settings
from core.logging import get_logger
from core.database import DecisionOutcome
from .real_time_monitor import create_realtime_monitor

logger = get_logger()


class PatientMonitoringAgent(BaseHealthcareAgent):
    """
    Patient monitoring agent

    Capabilities:
    1. Real-time vital signs monitoring
    2. Early warning system (sepsis, deterioration)
    3. Anomaly detection
    4. Trend analysis
    """

    def __init__(self, agent_id: str = "patient-monitor-001"):
        super().__init__(
            agent_id=agent_id,
            agent_type="patient_monitoring",
            agent_version="1.0.0"
        )

        # Initialize real-time monitor
        self.realtime_monitor = create_realtime_monitor()

        logger.info("Patient Monitoring Agent initialized")

    async def perceive(self, data: Dict[str, Any]) -> Observation:
        """
        Process patient monitoring request

        Expected input:
        {
            "patient_id": "uuid",
            "vital_signs": {...},
            "timestamp": "ISO datetime"
        }
        """

        required = ["patient_id"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return Observation(
            data=data,
            source="patient_monitoring_agent",
            patient_id=data.get("patient_id")
        )

    async def reason(self, observation: Observation) -> Decision:
        """
        Analyze patient vital signs

        Returns assessment and any alerts.
        """

        data = observation.data
        patient_id = data["patient_id"]
        vitals = data.get("vital_signs", {})

        # Perform assessment
        assessment = await self._assess_patient_status(patient_id, vitals)

        # Build decision
        decision = Decision(
            action="patient_assessment",
            parameters=assessment,
            confidence=assessment.get("confidence", 0.9),
            reasoning=[
                f"Analyzed {len(vitals)} vital signs",
                f"Status: {assessment.get('overall_status')}",
                f"Alerts generated: {len(assessment.get('alerts', []))}"
            ],
            knowledge_sources=["Vital signs thresholds", "SIRS criteria", "Early warning scores"],
            explanation=assessment.get("summary", "")
        )

        return decision

    async def act(self, decision: Decision) -> ActionResult:
        """Execute monitoring action"""

        try:
            assessment = decision.parameters

            output = {
                "patient_status": assessment.get("overall_status"),
                "alerts": assessment.get("alerts", []),
                "recommendations": assessment.get("recommendations", []),
                "early_warning_score": assessment.get("early_warning_score")
            }

            return ActionResult(
                success=True,
                outcome=DecisionOutcome.SUCCESS,
                details=output
            )

        except Exception as e:
            logger.error(f"Monitoring action failed: {e}")
            return ActionResult(
                success=False,
                outcome=DecisionOutcome.FAILURE,
                errors=[str(e)]
            )

    async def _assess_patient_status(
        self,
        patient_id: str,
        vitals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive patient status assessment

        Includes:
        - Vital signs evaluation
        - Early warning score (NEWS2)
        - Sepsis risk
        - Alerts
        """

        # Calculate NEWS2 score
        news2_score = self._calculate_news2(vitals)

        # Assess sepsis risk
        sepsis_risk = self._assess_sepsis(vitals)

        # Generate alerts
        alerts = []
        recommendations = []

        # NEWS2-based recommendations
        if news2_score >= 7:
            alerts.append({
                "severity": "CRITICAL",
                "type": "high_news2",
                "message": f"HIGH NEWS2 score: {news2_score}",
                "recommendation": "Urgent clinical review, consider ICU"
            })
            recommendations.append("Immediate physician assessment")
            recommendations.append("Consider ICU transfer")
            overall_status = "CRITICAL"

        elif news2_score >= 5:
            alerts.append({
                "severity": "WARNING",
                "type": "elevated_news2",
                "message": f"Elevated NEWS2 score: {news2_score}",
                "recommendation": "Urgent clinical review within 1 hour"
            })
            recommendations.append("Increased monitoring frequency")
            overall_status = "WARNING"

        elif news2_score >= 3:
            alerts.append({
                "severity": "INFO",
                "type": "moderate_news2",
                "message": f"Moderate NEWS2 score: {news2_score}",
                "recommendation": "Clinical review by competent nurse"
            })
            recommendations.append("Reassess vitals in 1 hour")
            overall_status = "STABLE"

        else:
            overall_status = "STABLE"

        # Sepsis alerts
        if sepsis_risk >= 0.7:
            alerts.append({
                "severity": "CRITICAL",
                "type": "high_sepsis_risk",
                "message": f"High sepsis risk: {sepsis_risk:.0%}",
                "recommendation": "Initiate sepsis protocol immediately"
            })
            recommendations.append("Blood cultures x2")
            recommendations.append("Lactate level")
            recommendations.append("Broad-spectrum antibiotics within 1 hour")

        return {
            "overall_status": overall_status,
            "early_warning_score": news2_score,
            "sepsis_risk": round(sepsis_risk, 2),
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": 0.9,
            "summary": f"Patient status: {overall_status}, NEWS2: {news2_score}, Sepsis risk: {sepsis_risk:.0%}"
        }

    def _calculate_news2(self, vitals: Dict[str, Any]) -> int:
        """
        Calculate NEWS2 (National Early Warning Score 2)

        Scoring system for detecting deteriorating patients.
        """

        score = 0

        # Respiratory rate
        rr = vitals.get("respiratory_rate")
        if rr:
            if rr <= 8:
                score += 3
            elif rr <= 11:
                score += 1
            elif rr <= 20:
                score += 0
            elif rr <= 24:
                score += 2
            else:
                score += 3

        # Oxygen saturation
        spo2 = vitals.get("oxygen_saturation")
        if spo2:
            if spo2 <= 91:
                score += 3
            elif spo2 <= 93:
                score += 2
            elif spo2 <= 95:
                score += 1
            else:
                score += 0

        # Systolic blood pressure
        sbp = vitals.get("blood_pressure_systolic")
        if sbp:
            if sbp <= 90:
                score += 3
            elif sbp <= 100:
                score += 2
            elif sbp <= 110:
                score += 1
            elif sbp <= 219:
                score += 0
            else:
                score += 3

        # Heart rate
        hr = vitals.get("heart_rate")
        if hr:
            if hr <= 40:
                score += 3
            elif hr <= 50:
                score += 1
            elif hr <= 90:
                score += 0
            elif hr <= 110:
                score += 1
            elif hr <= 130:
                score += 2
            else:
                score += 3

        # Temperature
        temp = vitals.get("temperature")
        if temp:
            if temp <= 35.0:
                score += 3
            elif temp <= 36.0:
                score += 1
            elif temp <= 38.0:
                score += 0
            elif temp <= 39.0:
                score += 1
            else:
                score += 2

        return score

    def _assess_sepsis(self, vitals: Dict[str, Any]) -> float:
        """
        Assess sepsis risk using qSOFA + SIRS criteria

        Returns probability (0-1)
        """

        sirs_score = 0

        # Temperature
        temp = vitals.get("temperature")
        if temp and (temp > 38.0 or temp < 36.0):
            sirs_score += 1

        # Heart rate
        hr = vitals.get("heart_rate")
        if hr and hr > 90:
            sirs_score += 1

        # Respiratory rate
        rr = vitals.get("respiratory_rate")
        if rr and rr > 20:
            sirs_score += 1

        # qSOFA score
        qsofa_score = 0

        # Respiratory rate >= 22
        if rr and rr >= 22:
            qsofa_score += 1

        # Altered mentation (can't assess from vitals alone)

        # Systolic BP <= 100
        sbp = vitals.get("blood_pressure_systolic")
        if sbp and sbp <= 100:
            qsofa_score += 1

        # Combined risk assessment
        # qSOFA >= 2: high risk
        # SIRS >= 2: moderate risk

        if qsofa_score >= 2:
            return 0.8
        elif sirs_score >= 2:
            return 0.5
        elif sirs_score >= 1:
            return 0.2
        else:
            return 0.1


def create_patient_monitoring_agent() -> PatientMonitoringAgent:
    """Create patient monitoring agent"""
    return PatientMonitoringAgent()
