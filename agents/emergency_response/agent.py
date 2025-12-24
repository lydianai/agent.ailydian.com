"""
Emergency Response Agent

Handles emergency triage, rapid assessment, and critical decision support.
Implements ESI (Emergency Severity Index) and rapid risk stratification.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from agents.base_agent import BaseAgent, AgentCapability
from core.logging import get_logger
from core.monitoring.metrics import (
    track_agent_performance,
    track_emergency_triage,
    track_protocol_activation,
)

logger = get_logger(__name__)


class TriageLevel(str, Enum):
    """ESI Triage Levels (Emergency Severity Index)"""
    LEVEL_1 = "level_1"  # Immediate life-saving intervention
    LEVEL_2 = "level_2"  # High risk, confusion, severe pain
    LEVEL_3 = "level_3"  # Stable but needs multiple resources
    LEVEL_4 = "level_4"  # Stable, needs one resource
    LEVEL_5 = "level_5"  # Non-urgent


class EmergencyType(str, Enum):
    """Types of emergency situations"""
    CARDIAC_ARREST = "cardiac_arrest"
    STROKE = "stroke"
    TRAUMA = "trauma"
    RESPIRATORY_FAILURE = "respiratory_failure"
    SEPTIC_SHOCK = "septic_shock"
    ANAPHYLAXIS = "anaphylaxis"
    HEMORRHAGE = "hemorrhage"
    ALTERED_MENTAL_STATUS = "altered_mental_status"
    CHEST_PAIN = "chest_pain"
    SEIZURE = "seizure"


class EmergencyResponseAgent(BaseAgent):
    """
    Emergency Response Agent

    Capabilities:
    - Rapid triage assessment (ESI 1-5)
    - ABCDE primary survey
    - Critical intervention recommendations
    - Resource mobilization
    - Time-sensitive protocol activation (stroke, STEMI, trauma)
    """

    def __init__(self):
        super().__init__(
            agent_id="emergency-response-agent",
            name="Emergency Response Agent",
            capabilities=[
                AgentCapability.TRIAGE,
                AgentCapability.EMERGENCY_PROTOCOLS,
                AgentCapability.CRITICAL_DECISION_SUPPORT,
            ],
        )

        # Critical time windows
        self.time_critical_conditions = {
            EmergencyType.CARDIAC_ARREST: 4,  # 4 minutes to CPR
            EmergencyType.STROKE: 60,  # 60 minutes to tPA
            EmergencyType.TRAUMA: 60,  # Golden hour
            EmergencyType.SEPTIC_SHOCK: 60,  # 1 hour antibiotics
        }

    async def perceive(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive emergency situation

        Args:
            environment_data: {
                "chief_complaint": str,
                "vital_signs": dict,
                "symptoms": list,
                "onset_time": datetime,
                "allergies": list,
                "medications": list,
                "medical_history": list,
            }

        Returns:
            Processed emergency data with risk indicators
        """
        chief_complaint = environment_data.get("chief_complaint", "")
        vital_signs = environment_data.get("vital_signs", {})
        symptoms = environment_data.get("symptoms", [])

        # Detect red flags
        red_flags = self._detect_red_flags(chief_complaint, vital_signs, symptoms)

        # Calculate vital sign abnormalities
        vital_abnormalities = self._assess_vital_abnormalities(vital_signs)

        return {
            "chief_complaint": chief_complaint,
            "vital_signs": vital_signs,
            "symptoms": symptoms,
            "red_flags": red_flags,
            "vital_abnormalities": vital_abnormalities,
            "time_received": datetime.utcnow(),
        }

    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about emergency situation and determine triage level

        Returns:
            Emergency assessment with triage level and recommendations
        """
        # ESI Triage Decision
        triage_level = await self._calculate_esi_level(perception)

        # Identify emergency type
        emergency_type = self._identify_emergency_type(perception)

        # ABCDE Assessment
        abcde_assessment = self._perform_abcde_assessment(perception)

        # Time-critical protocol check
        protocol_activation = await self._check_time_critical_protocols(
            emergency_type, perception
        )

        # Resource needs
        resources_needed = self._determine_resources(triage_level, emergency_type)

        # Critical interventions
        interventions = self._determine_critical_interventions(
            triage_level, emergency_type, abcde_assessment
        )

        return {
            "triage_level": triage_level,
            "emergency_type": emergency_type,
            "abcde_assessment": abcde_assessment,
            "protocol_activation": protocol_activation,
            "resources_needed": resources_needed,
            "critical_interventions": interventions,
            "confidence": self._calculate_confidence(perception),
        }

    async def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute emergency response actions

        Returns:
            Action plan with prioritized interventions
        """
        triage_level = reasoning["triage_level"]
        emergency_type = reasoning["emergency_type"]

        # Generate action plan
        action_plan = {
            "priority": self._get_priority_from_triage(triage_level),
            "immediate_actions": reasoning["critical_interventions"],
            "resource_mobilization": reasoning["resources_needed"],
            "protocols_activated": reasoning["protocol_activation"],
            "disposition": self._determine_disposition(triage_level, emergency_type),
            "estimated_time_to_physician": self._estimate_time_to_physician(triage_level),
        }

        # Log critical decision
        await self.log_decision(
            action=f"Emergency triage: {triage_level.value}",
            reasoning=reasoning,
            outcome=action_plan,
        )

        return action_plan

    # ========================================================================
    # ESI TRIAGE CALCULATION
    # ========================================================================

    async def _calculate_esi_level(self, perception: Dict[str, Any]) -> TriageLevel:
        """
        Calculate ESI (Emergency Severity Index) Level

        ESI Algorithm:
        1. Does patient require immediate life-saving intervention? → Level 1
        2. Is patient high risk, confused, severe pain, or in distress? → Level 2
        3. How many resources needed? (≥2 → Level 3, 1 → Level 4, 0 → Level 5)
        """
        vital_signs = perception["vital_signs"]
        red_flags = perception["red_flags"]
        vital_abnormalities = perception["vital_abnormalities"]

        # Level 1: Immediate life-saving intervention
        if self._requires_immediate_intervention(vital_signs, red_flags):
            return TriageLevel.LEVEL_1

        # Level 2: High risk situation
        if self._is_high_risk(vital_abnormalities, red_flags, perception):
            return TriageLevel.LEVEL_2

        # Level 3-5: Based on resource needs
        resources_needed = self._count_resources_needed(perception)

        if resources_needed >= 2:
            return TriageLevel.LEVEL_3
        elif resources_needed == 1:
            return TriageLevel.LEVEL_4
        else:
            return TriageLevel.LEVEL_5

    def _requires_immediate_intervention(
        self, vital_signs: dict, red_flags: list
    ) -> bool:
        """Check if patient needs immediate life-saving intervention"""

        # Cardiac arrest indicators
        if vital_signs.get("heart_rate", 100) < 40 or vital_signs.get("heart_rate", 100) > 150:
            if vital_signs.get("systolic_bp", 100) < 70:
                return True

        # Respiratory failure
        if vital_signs.get("respiratory_rate", 16) < 8 or vital_signs.get("respiratory_rate", 16) > 35:
            if vital_signs.get("spo2", 100) < 85:
                return True

        # Critical red flags
        critical_flags = [
            "unresponsive",
            "no_pulse",
            "not_breathing",
            "severe_hemorrhage",
            "airway_obstruction",
        ]

        return any(flag in red_flags for flag in critical_flags)

    def _is_high_risk(
        self, vital_abnormalities: dict, red_flags: list, perception: dict
    ) -> bool:
        """Check if patient is high risk (ESI Level 2)"""

        # Multiple vital sign abnormalities
        if vital_abnormalities.get("severe_count", 0) >= 2:
            return True

        # High-risk red flags
        high_risk_flags = [
            "chest_pain",
            "stroke_symptoms",
            "severe_pain",
            "altered_mental_status",
            "immunocompromised",
            "new_onset_confusion",
        ]

        if any(flag in red_flags for flag in high_risk_flags):
            return True

        # Age + vital signs (pediatric or geriatric with abnormal vitals)
        # Would need age data from perception

        return False

    def _count_resources_needed(self, perception: dict) -> int:
        """
        Count healthcare resources needed

        Resources include:
        - Lab tests (CBC, CMP, troponin, etc.)
        - Imaging (X-ray, CT, MRI, ultrasound)
        - IV fluids/medications
        - Procedures (sutures, splinting, etc.)
        - Specialist consultation
        """
        resources = 0
        symptoms = perception.get("symptoms", [])
        chief_complaint = perception.get("chief_complaint", "").lower()

        # Imaging likely needed
        imaging_keywords = ["trauma", "fracture", "head injury", "chest pain", "abdominal pain"]
        if any(keyword in chief_complaint for keyword in imaging_keywords):
            resources += 1

        # Lab work likely needed
        lab_keywords = ["chest pain", "abdominal pain", "fever", "weakness", "infection"]
        if any(keyword in chief_complaint for keyword in lab_keywords):
            resources += 1

        # IV fluids/meds likely needed
        if any(s in symptoms for s in ["dehydration", "severe_pain", "infection"]):
            resources += 1

        # Procedures needed
        procedure_keywords = ["laceration", "fracture", "dislocation"]
        if any(keyword in chief_complaint for keyword in procedure_keywords):
            resources += 1

        return min(resources, 4)  # Cap at 4 for practical purposes

    # ========================================================================
    # RED FLAG DETECTION
    # ========================================================================

    def _detect_red_flags(
        self, chief_complaint: str, vital_signs: dict, symptoms: list
    ) -> List[str]:
        """Detect critical red flags"""
        red_flags = []

        complaint_lower = chief_complaint.lower()

        # Cardiac red flags
        if "chest pain" in complaint_lower or "chest pressure" in complaint_lower:
            red_flags.append("chest_pain")

        # Stroke red flags (FAST)
        stroke_symptoms = ["facial droop", "arm weakness", "speech difficulty", "sudden confusion"]
        if any(s in symptoms for s in stroke_symptoms):
            red_flags.append("stroke_symptoms")

        # Trauma red flags
        if "trauma" in complaint_lower or "fall" in complaint_lower:
            red_flags.append("trauma")

        # Vital sign red flags
        if vital_signs.get("systolic_bp", 120) < 90:
            red_flags.append("hypotension")

        if vital_signs.get("spo2", 100) < 90:
            red_flags.append("hypoxia")

        if vital_signs.get("temperature", 37) > 38.5 or vital_signs.get("temperature", 37) < 35:
            red_flags.append("temperature_extreme")

        # Respiratory distress
        if vital_signs.get("respiratory_rate", 16) > 28 or vital_signs.get("respiratory_rate", 16) < 10:
            red_flags.append("respiratory_distress")

        # Altered mental status
        if any(s in symptoms for s in ["confusion", "unresponsive", "altered_mental_status"]):
            red_flags.append("altered_mental_status")

        return red_flags

    def _assess_vital_abnormalities(self, vital_signs: dict) -> dict:
        """Assess severity of vital sign abnormalities"""
        abnormalities = {
            "mild_count": 0,
            "moderate_count": 0,
            "severe_count": 0,
            "details": [],
        }

        # Heart rate
        hr = vital_signs.get("heart_rate", 75)
        if hr < 50:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_bradycardia")
        elif hr < 60:
            abnormalities["mild_count"] += 1
            abnormalities["details"].append("bradycardia")
        elif hr > 120:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_tachycardia")
        elif hr > 100:
            abnormalities["moderate_count"] += 1
            abnormalities["details"].append("tachycardia")

        # Blood pressure
        sbp = vital_signs.get("systolic_bp", 120)
        if sbp < 90:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_hypotension")
        elif sbp < 100:
            abnormalities["moderate_count"] += 1
            abnormalities["details"].append("hypotension")
        elif sbp > 180:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_hypertension")

        # SpO2
        spo2 = vital_signs.get("spo2", 98)
        if spo2 < 88:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_hypoxia")
        elif spo2 < 92:
            abnormalities["moderate_count"] += 1
            abnormalities["details"].append("hypoxia")

        # Respiratory rate
        rr = vital_signs.get("respiratory_rate", 16)
        if rr < 10 or rr > 30:
            abnormalities["severe_count"] += 1
            abnormalities["details"].append("severe_respiratory_abnormality")
        elif rr < 12 or rr > 24:
            abnormalities["moderate_count"] += 1
            abnormalities["details"].append("respiratory_abnormality")

        return abnormalities

    # ========================================================================
    # EMERGENCY TYPE IDENTIFICATION
    # ========================================================================

    def _identify_emergency_type(self, perception: dict) -> Optional[EmergencyType]:
        """Identify specific emergency type"""
        chief_complaint = perception.get("chief_complaint", "").lower()
        symptoms = perception.get("symptoms", [])
        vital_signs = perception.get("vital_signs", {})

        # Cardiac arrest
        if vital_signs.get("heart_rate", 75) == 0 or "no pulse" in symptoms:
            return EmergencyType.CARDIAC_ARREST

        # Stroke
        stroke_indicators = ["facial droop", "arm weakness", "speech difficulty"]
        if any(ind in symptoms for ind in stroke_indicators):
            return EmergencyType.STROKE

        # Trauma
        if "trauma" in chief_complaint or "fall" in chief_complaint or "accident" in chief_complaint:
            return EmergencyType.TRAUMA

        # Chest pain
        if "chest pain" in chief_complaint:
            return EmergencyType.CHEST_PAIN

        # Respiratory failure
        if vital_signs.get("spo2", 100) < 85 and vital_signs.get("respiratory_rate", 16) > 30:
            return EmergencyType.RESPIRATORY_FAILURE

        # Anaphylaxis
        if "allergic reaction" in symptoms or "anaphylaxis" in chief_complaint:
            return EmergencyType.ANAPHYLAXIS

        return None

    # ========================================================================
    # ABCDE ASSESSMENT
    # ========================================================================

    def _perform_abcde_assessment(self, perception: dict) -> dict:
        """
        ABCDE Primary Survey
        - Airway
        - Breathing
        - Circulation
        - Disability (neurological)
        - Exposure/Environment
        """
        vital_signs = perception.get("vital_signs", {})
        symptoms = perception.get("symptoms", [])

        return {
            "airway": self._assess_airway(symptoms),
            "breathing": self._assess_breathing(vital_signs),
            "circulation": self._assess_circulation(vital_signs),
            "disability": self._assess_disability(symptoms),
            "exposure": {},  # Would need additional data
        }

    def _assess_airway(self, symptoms: list) -> dict:
        """Assess airway patency"""
        if "stridor" in symptoms or "choking" in symptoms:
            return {"status": "compromised", "intervention_needed": True}
        return {"status": "patent", "intervention_needed": False}

    def _assess_breathing(self, vital_signs: dict) -> dict:
        """Assess breathing adequacy"""
        rr = vital_signs.get("respiratory_rate", 16)
        spo2 = vital_signs.get("spo2", 98)

        if rr < 10 or rr > 30 or spo2 < 90:
            return {
                "status": "inadequate",
                "intervention_needed": True,
                "oxygen_required": spo2 < 92,
            }

        return {"status": "adequate", "intervention_needed": False}

    def _assess_circulation(self, vital_signs: dict) -> dict:
        """Assess circulatory status"""
        hr = vital_signs.get("heart_rate", 75)
        sbp = vital_signs.get("systolic_bp", 120)

        if sbp < 90 or hr > 120:
            return {
                "status": "compromised",
                "intervention_needed": True,
                "fluid_resuscitation": sbp < 90,
            }

        return {"status": "adequate", "intervention_needed": False}

    def _assess_disability(self, symptoms: list) -> dict:
        """Assess neurological status"""
        if any(s in symptoms for s in ["confusion", "unresponsive", "altered_mental_status"]):
            return {"status": "impaired", "gcs_estimate": "<15"}

        return {"status": "normal", "gcs_estimate": "15"}

    # ========================================================================
    # PROTOCOL ACTIVATION
    # ========================================================================

    async def _check_time_critical_protocols(
        self, emergency_type: Optional[EmergencyType], perception: dict
    ) -> List[dict]:
        """Check if time-critical protocols should be activated"""
        protocols = []

        if not emergency_type:
            return protocols

        if emergency_type == EmergencyType.STROKE:
            protocols.append({
                "protocol": "Stroke Alert",
                "time_window": "60 minutes to tPA",
                "actions": [
                    "Activate stroke team",
                    "Stat CT head",
                    "Check tPA eligibility",
                    "Notify neurology",
                ],
            })

        if emergency_type == EmergencyType.CHEST_PAIN:
            protocols.append({
                "protocol": "STEMI Alert",
                "time_window": "90 minutes door-to-balloon",
                "actions": [
                    "12-lead ECG within 10 minutes",
                    "Troponin, CK-MB",
                    "Aspirin 325mg",
                    "Alert cath lab if STEMI",
                ],
            })

        if emergency_type == EmergencyType.TRAUMA:
            protocols.append({
                "protocol": "Trauma Activation",
                "time_window": "Golden hour",
                "actions": [
                    "Activate trauma team",
                    "FAST ultrasound",
                    "Massive transfusion protocol ready",
                    "Notify OR",
                ],
            })

        if emergency_type == EmergencyType.SEPTIC_SHOCK:
            protocols.append({
                "protocol": "Sepsis Bundle",
                "time_window": "1 hour to antibiotics",
                "actions": [
                    "Blood cultures x2",
                    "Lactate level",
                    "Broad-spectrum antibiotics",
                    "30 mL/kg fluid bolus if hypotensive",
                ],
            })

        return protocols

    # ========================================================================
    # RESOURCE DETERMINATION
    # ========================================================================

    def _determine_resources(
        self, triage_level: TriageLevel, emergency_type: Optional[EmergencyType]
    ) -> dict:
        """Determine resources needed"""
        resources = {
            "staff": [],
            "equipment": [],
            "location": "",
        }

        if triage_level == TriageLevel.LEVEL_1:
            resources["staff"] = ["Physician", "2 Nurses", "Respiratory Therapist"]
            resources["equipment"] = ["Crash cart", "Ventilator", "Monitors"]
            resources["location"] = "Resuscitation Bay"

        elif triage_level == TriageLevel.LEVEL_2:
            resources["staff"] = ["Physician", "Nurse"]
            resources["equipment"] = ["Monitors", "IV access"]
            resources["location"] = "Acute Care Area"

        else:
            resources["staff"] = ["Nurse", "Physician (when available)"]
            resources["equipment"] = []
            resources["location"] = "General ED"

        return resources

    def _determine_critical_interventions(
        self,
        triage_level: TriageLevel,
        emergency_type: Optional[EmergencyType],
        abcde: dict,
    ) -> List[str]:
        """Determine critical interventions needed"""
        interventions = []

        # ABCs take priority
        if abcde["airway"]["intervention_needed"]:
            interventions.append("Secure airway")

        if abcde["breathing"]["intervention_needed"]:
            if abcde["breathing"].get("oxygen_required"):
                interventions.append("Supplemental oxygen")

        if abcde["circulation"]["intervention_needed"]:
            if abcde["circulation"].get("fluid_resuscitation"):
                interventions.append("IV access + fluid resuscitation")

        # Emergency-specific interventions
        if emergency_type == EmergencyType.CARDIAC_ARREST:
            interventions.extend(["Start CPR", "Attach AED/defibrillator", "Epinephrine"])

        elif emergency_type == EmergencyType.ANAPHYLAXIS:
            interventions.extend(["IM Epinephrine 0.3mg", "IV antihistamines", "Steroids"])

        return interventions

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_priority_from_triage(self, triage_level: TriageLevel) -> str:
        """Get priority level from triage"""
        priority_map = {
            TriageLevel.LEVEL_1: "CRITICAL",
            TriageLevel.LEVEL_2: "EMERGENT",
            TriageLevel.LEVEL_3: "URGENT",
            TriageLevel.LEVEL_4: "LESS_URGENT",
            TriageLevel.LEVEL_5: "NON_URGENT",
        }
        return priority_map.get(triage_level, "URGENT")

    def _determine_disposition(
        self, triage_level: TriageLevel, emergency_type: Optional[EmergencyType]
    ) -> str:
        """Determine likely patient disposition"""
        if triage_level == TriageLevel.LEVEL_1:
            return "ICU admission likely"
        elif triage_level == TriageLevel.LEVEL_2:
            return "Hospital admission possible"
        else:
            return "Discharge likely after evaluation"

    def _estimate_time_to_physician(self, triage_level: TriageLevel) -> str:
        """Estimate time until physician evaluation"""
        time_map = {
            TriageLevel.LEVEL_1: "Immediate",
            TriageLevel.LEVEL_2: "< 10 minutes",
            TriageLevel.LEVEL_3: "< 30 minutes",
            TriageLevel.LEVEL_4: "< 60 minutes",
            TriageLevel.LEVEL_5: "< 120 minutes",
        }
        return time_map.get(triage_level, "< 60 minutes")

    def _calculate_confidence(self, perception: dict) -> float:
        """Calculate confidence in assessment"""
        # Higher confidence with more complete data
        data_completeness = 0
        required_fields = ["chief_complaint", "vital_signs", "symptoms"]

        for field in required_fields:
            if perception.get(field):
                data_completeness += 1

        return data_completeness / len(required_fields)

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    @track_agent_performance("Emergency Response Agent")
    async def triage_patient(
        self,
        chief_complaint: str,
        vital_signs: dict,
        symptoms: List[str],
        onset_time: Optional[datetime] = None,
        medical_history: Optional[List[str]] = None,
    ) -> dict:
        """
        Main entry point for emergency triage

        Args:
            chief_complaint: Patient's chief complaint
            vital_signs: Current vital signs
            symptoms: List of symptoms
            onset_time: When symptoms started
            medical_history: Past medical history

        Returns:
            Complete triage assessment with action plan
        """
        # Build environment data
        environment_data = {
            "chief_complaint": chief_complaint,
            "vital_signs": vital_signs,
            "symptoms": symptoms,
            "onset_time": onset_time or datetime.utcnow(),
            "medical_history": medical_history or [],
        }

        # Execute agent cycle
        perception = await self.perceive(environment_data)
        reasoning = await self.reason(perception)
        action_plan = await self.act(reasoning)

        # Track metrics
        triage_level_str = reasoning["triage_level"].value
        emergency_type_str = reasoning["emergency_type"].value if reasoning["emergency_type"] else "unknown"

        track_emergency_triage(triage_level_str, emergency_type_str)

        # Track protocol activations
        for protocol in action_plan["protocols_activated"]:
            track_protocol_activation(protocol["protocol"])

        # Combine results
        return {
            "triage_level": triage_level_str,
            "priority": action_plan["priority"],
            "emergency_type": emergency_type_str,
            "action_plan": action_plan,
            "abcde_assessment": reasoning["abcde_assessment"],
            "red_flags": perception["red_flags"],
            "protocols_activated": action_plan["protocols_activated"],
            "confidence": reasoning["confidence"],
            "timestamp": perception["time_received"].isoformat(),
        }
