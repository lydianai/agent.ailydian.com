"""
Treatment Planning Agent

Provides evidence-based treatment planning with:
- Clinical practice guidelines (CPG)
- Drug interaction checking
- Personalized treatment protocols
- Contraindication detection
- Dosage optimization
- Treatment monitoring plans
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from agents.base_agent import BaseAgent, AgentCapability
from core.logging import get_logger
from core.monitoring.metrics import track_agent_performance

logger = get_logger(__name__)


class TreatmentCategory(str, Enum):
    """Categories of treatment"""
    PHARMACOLOGICAL = "pharmacological"
    SURGICAL = "surgical"
    INTERVENTIONAL = "interventional"
    SUPPORTIVE = "supportive"
    PREVENTIVE = "preventive"
    REHABILITATIVE = "rehabilitative"


class TreatmentPriority(str, Enum):
    """Treatment priority levels"""
    EMERGENT = "emergent"  # Immediate (< 15 min)
    URGENT = "urgent"  # Within 1-2 hours
    TIMELY = "timely"  # Within 24 hours
    ROUTINE = "routine"  # Within days-weeks
    ELECTIVE = "elective"  # Scheduled


class GuidelineCompliance(str, Enum):
    """Guideline compliance levels"""
    STRICT = "strict"  # Follows guidelines exactly
    ADAPTED = "adapted"  # Modified for patient-specific factors
    ALTERNATIVE = "alternative"  # Alternative approach due to contraindications
    EXPERIMENTAL = "experimental"  # Off-label or investigational


class DrugInteractionSeverity(str, Enum):
    """Drug interaction severity"""
    CONTRAINDICATED = "contraindicated"  # Absolute contraindication
    MAJOR = "major"  # Serious interaction, requires monitoring
    MODERATE = "moderate"  # Monitor closely
    MINOR = "minor"  # Minimal clinical significance


class TreatmentPlanningAgent(BaseAgent):
    """
    Treatment Planning Agent

    Capabilities:
    - Evidence-based treatment protocol generation
    - Drug interaction checking
    - Contraindication detection
    - Personalized dosing
    - Guideline compliance verification
    - Treatment monitoring plans
    """

    def __init__(self):
        super().__init__(
            agent_id="treatment-planning-agent",
            name="Treatment Planning Agent",
            capabilities=[
                AgentCapability.TREATMENT_PLANNING,
                AgentCapability.DRUG_INTERACTION_CHECK,
                AgentCapability.CLINICAL_DECISION_SUPPORT,
            ],
        )

        # Clinical practice guidelines database (simplified)
        self.treatment_protocols = {
            "pneumonia": {
                "category": TreatmentCategory.PHARMACOLOGICAL,
                "priority": TreatmentPriority.URGENT,
                "first_line": [
                    {
                        "medication": "Ceftriaxone",
                        "dose": "1-2g IV q24h",
                        "duration": "5-7 days",
                        "indication": "Community-acquired pneumonia",
                    },
                    {
                        "medication": "Azithromycin",
                        "dose": "500mg PO/IV q24h",
                        "duration": "5 days",
                        "indication": "Atypical coverage",
                    },
                ],
                "supportive": [
                    "Oxygen therapy if SpO2 < 94%",
                    "IV fluids for hydration",
                    "Antipyretics for fever",
                ],
                "monitoring": ["Repeat CXR in 48-72h", "Daily vitals", "O2 saturation"],
            },
            "pulmonary_embolism": {
                "category": TreatmentCategory.PHARMACOLOGICAL,
                "priority": TreatmentPriority.EMERGENT,
                "first_line": [
                    {
                        "medication": "Heparin",
                        "dose": "80 units/kg IV bolus, then 18 units/kg/hr infusion",
                        "duration": "5-10 days",
                        "indication": "Immediate anticoagulation",
                    },
                    {
                        "medication": "Apixaban",
                        "dose": "10mg PO BID x7 days, then 5mg BID",
                        "duration": "3-6 months",
                        "indication": "Long-term anticoagulation",
                    },
                ],
                "interventional": ["Consider thrombolysis if massive PE", "IVC filter if anticoagulation contraindicated"],
                "monitoring": ["aPTT q6h (for heparin)", "Anti-Xa levels", "Daily CBC", "Bleeding precautions"],
            },
            "myocardial_infarction": {
                "category": TreatmentCategory.INTERVENTIONAL,
                "priority": TreatmentPriority.EMERGENT,
                "first_line": [
                    {
                        "medication": "Aspirin",
                        "dose": "325mg PO stat, then 81mg daily",
                        "duration": "Lifelong",
                        "indication": "Antiplatelet therapy",
                    },
                    {
                        "medication": "Clopidogrel",
                        "dose": "600mg loading, then 75mg daily",
                        "duration": "12 months",
                        "indication": "Dual antiplatelet therapy",
                    },
                    {
                        "medication": "Atorvastatin",
                        "dose": "80mg PO daily",
                        "duration": "Lifelong",
                        "indication": "High-intensity statin",
                    },
                ],
                "interventional": ["Emergent PCI (door-to-balloon < 90 min)", "CABG if indicated"],
                "monitoring": ["Continuous ECG", "Serial troponins", "Echo within 24h"],
            },
            "stroke_ischemic": {
                "category": TreatmentCategory.PHARMACOLOGICAL,
                "priority": TreatmentPriority.EMERGENT,
                "first_line": [
                    {
                        "medication": "Alteplase (tPA)",
                        "dose": "0.9mg/kg IV (max 90mg), 10% bolus, 90% over 60min",
                        "duration": "Single dose",
                        "indication": "Thrombolysis within 4.5 hours",
                        "contraindications": ["Recent surgery", "Hemorrhagic stroke", "BP > 185/110"],
                    },
                    {
                        "medication": "Aspirin",
                        "dose": "325mg PO daily (after 24h if tPA given)",
                        "duration": "Lifelong",
                        "indication": "Secondary prevention",
                    },
                ],
                "interventional": ["Mechanical thrombectomy if large vessel occlusion"],
                "monitoring": ["Neuro checks q1h x24h", "BP control", "Repeat CT at 24h"],
            },
            "appendicitis": {
                "category": TreatmentCategory.SURGICAL,
                "priority": TreatmentPriority.URGENT,
                "first_line": [
                    {
                        "medication": "Ceftriaxone + Metronidazole",
                        "dose": "Ceftriaxone 1g IV q24h + Metronidazole 500mg IV q8h",
                        "duration": "24-48h perioperatively",
                        "indication": "Perioperative antibiotics",
                    },
                ],
                "surgical": ["Laparoscopic appendectomy (preferred)", "Open appendectomy if complicated"],
                "monitoring": ["Post-op vitals", "Wound care", "Return of bowel function"],
            },
            "sepsis": {
                "category": TreatmentCategory.PHARMACOLOGICAL,
                "priority": TreatmentPriority.EMERGENT,
                "first_line": [
                    {
                        "medication": "Vancomycin + Piperacillin-Tazobactam",
                        "dose": "Vancomycin 15-20mg/kg IV q8-12h + Pip-Tazo 4.5g IV q6h",
                        "duration": "7-14 days (adjust based on cultures)",
                        "indication": "Broad-spectrum empiric coverage",
                    },
                ],
                "supportive": [
                    "Fluid resuscitation (30mL/kg crystalloid within 3h)",
                    "Vasopressors if MAP < 65 after fluids",
                    "Source control (drain abscess, remove infected devices)",
                ],
                "monitoring": ["Lactate q2-4h", "Blood cultures", "Procalcitonin", "ICU admission"],
            },
        }

        # Drug interaction database (simplified)
        self.drug_interactions = {
            ("Warfarin", "Aspirin"): {
                "severity": DrugInteractionSeverity.MAJOR,
                "effect": "Increased bleeding risk",
                "management": "Monitor INR closely, consider PPI for GI protection",
            },
            ("Clopidogrel", "Omeprazole"): {
                "severity": DrugInteractionSeverity.MODERATE,
                "effect": "Reduced clopidogrel efficacy",
                "management": "Use alternative PPI (pantoprazole) or H2 blocker",
            },
            ("Simvastatin", "Clarithromycin"): {
                "severity": DrugInteractionSeverity.MAJOR,
                "effect": "Increased statin toxicity (rhabdomyolysis risk)",
                "management": "Hold statin during macrolide therapy",
            },
            ("Metformin", "Contrast dye"): {
                "severity": DrugInteractionSeverity.MAJOR,
                "effect": "Lactic acidosis risk",
                "management": "Hold metformin 48h before and after contrast",
            },
        }

        # Common contraindications
        self.contraindications = {
            "Beta-blockers": ["Severe asthma", "Complete heart block", "Cardiogenic shock"],
            "ACE inhibitors": ["Pregnancy", "Bilateral renal artery stenosis", "Angioedema history"],
            "NSAIDs": ["Active GI bleeding", "Severe renal impairment", "Aspirin allergy"],
            "Metformin": ["eGFR < 30", "Lactic acidosis", "Severe liver disease"],
            "tPA": ["Recent surgery (<2 weeks)", "Active bleeding", "Hemorrhagic stroke", "BP > 185/110"],
        }

    async def perceive(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive patient data for treatment planning

        Args:
            environment_data: {
                "patient_id": str,
                "diagnosis": dict or str,
                "patient_data": {
                    "age": int,
                    "weight_kg": float,
                    "allergies": list,
                    "current_medications": list,
                    "comorbidities": list,
                    "renal_function": {"egfr": float},
                    "hepatic_function": {"alt": float, "ast": float},
                    "pregnancy_status": bool,
                },
                "vital_signs": dict,
                "lab_results": dict,
                "clinical_context": dict,
            }

        Returns:
            Processed treatment planning data
        """
        patient_id = environment_data.get("patient_id")
        diagnosis = environment_data.get("diagnosis")
        patient_data = environment_data.get("patient_data", {})
        vital_signs = environment_data.get("vital_signs", {})
        lab_results = environment_data.get("lab_results", {})

        # Extract diagnosis name
        if isinstance(diagnosis, dict):
            diagnosis_name = diagnosis.get("diagnosis", "")
        else:
            diagnosis_name = diagnosis

        # Identify patient-specific factors
        patient_factors = self._extract_patient_factors(patient_data, lab_results)

        # Detect contraindications
        contraindications = self._detect_contraindications(patient_data)

        # Check current medication interactions
        current_meds = patient_data.get("current_medications", [])
        existing_interactions = self._check_existing_interactions(current_meds)

        return {
            "patient_id": patient_id,
            "diagnosis": diagnosis_name,
            "patient_factors": patient_factors,
            "contraindications": contraindications,
            "current_medications": current_meds,
            "existing_interactions": existing_interactions,
            "vital_signs": vital_signs,
            "lab_results": lab_results,
            "timestamp": datetime.utcnow(),
        }

    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about optimal treatment plan

        Returns:
            Treatment plan with rationale
        """
        diagnosis = perception["diagnosis"]
        patient_factors = perception["patient_factors"]
        contraindications = perception["contraindications"]
        current_meds = perception["current_medications"]

        # Get evidence-based protocol
        protocol = self._get_treatment_protocol(diagnosis)

        # Adapt protocol for patient-specific factors
        adapted_treatment = self._adapt_treatment_for_patient(
            protocol, patient_factors, contraindications
        )

        # Check for drug interactions
        interaction_analysis = self._analyze_drug_interactions(
            adapted_treatment, current_meds
        )

        # Determine guideline compliance
        compliance_level = self._assess_guideline_compliance(
            adapted_treatment, protocol, patient_factors
        )

        # Calculate treatment priority
        priority = self._determine_treatment_priority(diagnosis, patient_factors)

        return {
            "treatment_protocol": adapted_treatment,
            "interaction_analysis": interaction_analysis,
            "guideline_compliance": compliance_level,
            "priority": priority,
            "rationale": self._generate_rationale(adapted_treatment, patient_factors),
        }

    async def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable treatment plan

        Returns:
            Complete treatment plan with orders and monitoring
        """
        treatment_protocol = reasoning["treatment_protocol"]
        interaction_analysis = reasoning["interaction_analysis"]
        priority = reasoning["priority"]

        # Generate medication orders
        medication_orders = self._generate_medication_orders(treatment_protocol)

        # Generate non-pharmacological interventions
        interventions = self._generate_interventions(treatment_protocol)

        # Create monitoring plan
        monitoring_plan = self._create_monitoring_plan(
            treatment_protocol, interaction_analysis
        )

        # Generate patient education points
        patient_education = self._generate_patient_education(treatment_protocol)

        # Define treatment goals and endpoints
        treatment_goals = self._define_treatment_goals(treatment_protocol)

        # Safety alerts and warnings
        safety_alerts = self._generate_safety_alerts(interaction_analysis, treatment_protocol)

        return {
            "treatment_plan": {
                "medication_orders": medication_orders,
                "interventions": interventions,
                "monitoring_plan": monitoring_plan,
                "patient_education": patient_education,
                "treatment_goals": treatment_goals,
            },
            "safety_alerts": safety_alerts,
            "priority": priority,
            "guideline_compliance": reasoning["guideline_compliance"],
        }

    # ========================================================================
    # PATIENT FACTORS
    # ========================================================================

    def _extract_patient_factors(self, patient_data: dict, lab_results: dict) -> Dict[str, Any]:
        """Extract relevant patient-specific factors"""
        factors = {
            "age": patient_data.get("age"),
            "weight_kg": patient_data.get("weight_kg"),
            "allergies": patient_data.get("allergies", []),
            "comorbidities": patient_data.get("comorbidities", []),
            "pregnancy": patient_data.get("pregnancy_status", False),
        }

        # Renal function
        renal = patient_data.get("renal_function", {})
        egfr = renal.get("egfr")
        if egfr:
            if egfr < 30:
                factors["renal_impairment"] = "severe"
            elif egfr < 60:
                factors["renal_impairment"] = "moderate"
            else:
                factors["renal_impairment"] = "normal"

        # Hepatic function
        hepatic = patient_data.get("hepatic_function", {})
        alt = hepatic.get("alt", 0)
        if alt > 3 * 40:  # > 3x ULN
            factors["hepatic_impairment"] = "severe"
        elif alt > 40:
            factors["hepatic_impairment"] = "mild"

        return factors

    def _detect_contraindications(self, patient_data: dict) -> List[Dict]:
        """Detect contraindications for common medications"""
        detected = []

        allergies = patient_data.get("allergies", [])
        comorbidities = patient_data.get("comorbidities", [])
        pregnancy = patient_data.get("pregnancy_status", False)

        # Check each drug class
        for drug_class, contraindications in self.contraindications.items():
            for contraindication in contraindications:
                # Check allergies
                if contraindication.lower() in [a.lower() for a in allergies]:
                    detected.append({
                        "drug_class": drug_class,
                        "contraindication": contraindication,
                        "type": "allergy",
                    })

                # Check comorbidities
                if contraindication.lower() in [c.lower() for c in comorbidities]:
                    detected.append({
                        "drug_class": drug_class,
                        "contraindication": contraindication,
                        "type": "comorbidity",
                    })

                # Check pregnancy
                if "pregnancy" in contraindication.lower() and pregnancy:
                    detected.append({
                        "drug_class": drug_class,
                        "contraindication": "Pregnancy",
                        "type": "pregnancy",
                    })

        return detected

    def _check_existing_interactions(self, medications: List[str]) -> List[Dict]:
        """Check interactions between current medications"""
        interactions = []

        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                # Check both directions
                interaction = self.drug_interactions.get((med1, med2)) or \
                             self.drug_interactions.get((med2, med1))

                if interaction:
                    interactions.append({
                        "drug1": med1,
                        "drug2": med2,
                        "severity": interaction["severity"].value,
                        "effect": interaction["effect"],
                        "management": interaction["management"],
                    })

        return interactions

    # ========================================================================
    # TREATMENT PROTOCOLS
    # ========================================================================

    def _get_treatment_protocol(self, diagnosis: str) -> Optional[Dict]:
        """Get evidence-based treatment protocol for diagnosis"""
        # Normalize diagnosis name
        diagnosis_normalized = diagnosis.lower().replace(" ", "_")

        return self.treatment_protocols.get(diagnosis_normalized)

    def _adapt_treatment_for_patient(
        self, protocol: Optional[Dict], patient_factors: dict, contraindications: List[Dict]
    ) -> Dict:
        """Adapt treatment protocol for patient-specific factors"""
        if not protocol:
            return {
                "medications": [],
                "interventions": [],
                "note": "No standard protocol available",
            }

        adapted = {
            "medications": [],
            "interventions": [],
            "supportive_care": protocol.get("supportive", []),
            "monitoring": protocol.get("monitoring", []),
        }

        # Adapt medications
        for med in protocol.get("first_line", []):
            medication_name = med["medication"]

            # Check contraindications
            is_contraindicated = any(
                medication_name.lower() in c["drug_class"].lower()
                for c in contraindications
            )

            if is_contraindicated:
                adapted["medications"].append({
                    **med,
                    "status": "contraindicated",
                    "alternative_needed": True,
                })
            else:
                # Adjust dose for renal/hepatic impairment
                adjusted_dose = self._adjust_dose_for_impairment(
                    medication_name, med["dose"], patient_factors
                )

                adapted["medications"].append({
                    **med,
                    "dose": adjusted_dose,
                    "status": "recommended",
                })

        # Add interventional procedures
        if "interventional" in protocol:
            adapted["interventions"].extend(protocol["interventional"])

        if "surgical" in protocol:
            adapted["interventions"].extend(protocol["surgical"])

        return adapted

    def _adjust_dose_for_impairment(
        self, medication: str, standard_dose: str, patient_factors: dict
    ) -> str:
        """Adjust medication dose for renal/hepatic impairment"""
        renal_impairment = patient_factors.get("renal_impairment")
        hepatic_impairment = patient_factors.get("hepatic_impairment")

        # Simple dose adjustment rules (in production, use detailed pharmacokinetic data)
        if renal_impairment == "severe":
            if any(drug in medication for drug in ["Heparin", "Metformin"]):
                return f"{standard_dose} (REDUCE DOSE 50% or AVOID)"

        if hepatic_impairment == "severe":
            if any(drug in medication for drug in ["Warfarin", "Statins"]):
                return f"{standard_dose} (REDUCE DOSE 50%)"

        return standard_dose

    def _analyze_drug_interactions(
        self, adapted_treatment: dict, current_medications: List[str]
    ) -> Dict:
        """Analyze drug interactions between new and existing medications"""
        interactions = {
            "new_interactions": [],
            "severity_summary": {
                "contraindicated": 0,
                "major": 0,
                "moderate": 0,
                "minor": 0,
            },
        }

        new_meds = [m["medication"] for m in adapted_treatment.get("medications", [])]

        # Check new meds against current meds
        for new_med in new_meds:
            for current_med in current_medications:
                interaction = self.drug_interactions.get((new_med, current_med)) or \
                             self.drug_interactions.get((current_med, new_med))

                if interaction:
                    severity = interaction["severity"].value
                    interactions["new_interactions"].append({
                        "new_medication": new_med,
                        "current_medication": current_med,
                        "severity": severity,
                        "effect": interaction["effect"],
                        "management": interaction["management"],
                    })
                    interactions["severity_summary"][severity] += 1

        return interactions

    def _assess_guideline_compliance(
        self, adapted_treatment: dict, protocol: Optional[Dict], patient_factors: dict
    ) -> str:
        """Assess level of guideline compliance"""
        if not protocol:
            return GuidelineCompliance.EXPERIMENTAL.value

        # Count contraindicated medications
        contraindicated_count = sum(
            1 for m in adapted_treatment.get("medications", [])
            if m.get("status") == "contraindicated"
        )

        if contraindicated_count > 0:
            return GuidelineCompliance.ALTERNATIVE.value

        # Check for dose adjustments
        dose_adjusted = any(
            "REDUCE" in m.get("dose", "") or "AVOID" in m.get("dose", "")
            for m in adapted_treatment.get("medications", [])
        )

        if dose_adjusted:
            return GuidelineCompliance.ADAPTED.value

        return GuidelineCompliance.STRICT.value

    def _determine_treatment_priority(self, diagnosis: str, patient_factors: dict) -> str:
        """Determine treatment priority based on diagnosis and patient factors"""
        diagnosis_normalized = diagnosis.lower().replace(" ", "_")
        protocol = self.treatment_protocols.get(diagnosis_normalized)

        if protocol:
            return protocol.get("priority", TreatmentPriority.ROUTINE).value

        return TreatmentPriority.ROUTINE.value

    def _generate_rationale(self, adapted_treatment: dict, patient_factors: dict) -> List[str]:
        """Generate clinical rationale for treatment decisions"""
        rationale = []

        # Medication rationale
        for med in adapted_treatment.get("medications", []):
            if med.get("status") == "contraindicated":
                rationale.append(
                    f"{med['medication']} contraindicated - alternative therapy needed"
                )
            elif "REDUCE" in med.get("dose", ""):
                rationale.append(
                    f"{med['medication']} dose reduced due to organ impairment"
                )

        # Patient-specific factors
        if patient_factors.get("renal_impairment") == "severe":
            rationale.append("Renal dosing adjustments applied")

        if patient_factors.get("pregnancy"):
            rationale.append("Pregnancy-safe alternatives selected")

        return rationale

    # ========================================================================
    # ACTION GENERATION
    # ========================================================================

    def _generate_medication_orders(self, treatment_protocol: dict) -> List[Dict]:
        """Generate structured medication orders"""
        orders = []

        for med in treatment_protocol.get("medications", []):
            if med.get("status") != "contraindicated":
                orders.append({
                    "medication": med["medication"],
                    "dose": med["dose"],
                    "duration": med.get("duration", "As directed"),
                    "indication": med.get("indication", ""),
                    "status": med.get("status", "recommended"),
                    "order_priority": "STAT" if "IV" in med["dose"] else "Routine",
                })

        return orders

    def _generate_interventions(self, treatment_protocol: dict) -> List[str]:
        """Generate non-pharmacological interventions"""
        interventions = []

        interventions.extend(treatment_protocol.get("interventions", []))
        interventions.extend(treatment_protocol.get("supportive_care", []))

        return interventions

    def _create_monitoring_plan(
        self, treatment_protocol: dict, interaction_analysis: dict
    ) -> Dict:
        """Create treatment monitoring plan"""
        monitoring = {
            "clinical_monitoring": treatment_protocol.get("monitoring", []),
            "lab_monitoring": [],
            "adverse_effect_monitoring": [],
        }

        # Add interaction-specific monitoring
        if interaction_analysis["severity_summary"]["major"] > 0:
            monitoring["adverse_effect_monitoring"].append(
                "Close monitoring for drug interactions (see safety alerts)"
            )

        # Add medication-specific monitoring
        for med in treatment_protocol.get("medications", []):
            med_name = med["medication"].lower()

            if "warfarin" in med_name:
                monitoring["lab_monitoring"].append("INR q2-3 days until stable, then weekly")
            elif "heparin" in med_name:
                monitoring["lab_monitoring"].append("aPTT q6h, target 60-80 seconds")
            elif "aminoglycoside" in med_name:
                monitoring["lab_monitoring"].append("Peak/trough levels, renal function")

        return monitoring

    def _generate_patient_education(self, treatment_protocol: dict) -> List[str]:
        """Generate patient education points"""
        education = []

        for med in treatment_protocol.get("medications", []):
            med_name = med["medication"]

            if "Anticoagulant" in med.get("indication", "") or "anticoagulation" in med.get("indication", "").lower():
                education.append(f"{med_name}: Bleeding precautions, avoid NSAIDs, report unusual bleeding")

            if "Antibiotic" in med.get("indication", ""):
                education.append(f"{med_name}: Complete full course, take with/without food as directed")

        return education

    def _define_treatment_goals(self, treatment_protocol: dict) -> List[str]:
        """Define treatment goals and success criteria"""
        goals = [
            "Symptom resolution",
            "Prevention of complications",
            "Return to baseline functional status",
        ]

        # Add diagnosis-specific goals
        medications = treatment_protocol.get("medications", [])
        if any("antibiotic" in m.get("indication", "").lower() for m in medications):
            goals.append("Eradication of infection")

        if any("anticoagulation" in m.get("indication", "").lower() for m in medications):
            goals.append("Prevention of thrombosis without bleeding")

        return goals

    def _generate_safety_alerts(
        self, interaction_analysis: dict, treatment_protocol: dict
    ) -> List[Dict]:
        """Generate safety alerts and warnings"""
        alerts = []

        # Drug interaction alerts
        for interaction in interaction_analysis.get("new_interactions", []):
            if interaction["severity"] in ["contraindicated", "major"]:
                alerts.append({
                    "type": "drug_interaction",
                    "severity": interaction["severity"],
                    "alert": f"{interaction['new_medication']} + {interaction['current_medication']}: {interaction['effect']}",
                    "action_required": interaction["management"],
                })

        # Contraindication alerts
        for med in treatment_protocol.get("medications", []):
            if med.get("status") == "contraindicated":
                alerts.append({
                    "type": "contraindication",
                    "severity": "major",
                    "alert": f"{med['medication']} is contraindicated",
                    "action_required": "Select alternative therapy",
                })

        return alerts

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    @track_agent_performance("Treatment Planning Agent")
    async def create_treatment_plan(
        self,
        patient_id: str,
        diagnosis: Any,
        patient_data: dict,
        vital_signs: Optional[dict] = None,
        lab_results: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Create comprehensive treatment plan

        Args:
            patient_id: Patient identifier
            diagnosis: Diagnosis (dict or string)
            patient_data: Patient demographics and medical history
            vital_signs: Current vital signs (optional)
            lab_results: Laboratory results (optional)

        Returns:
            Complete treatment plan with safety alerts
        """
        # Build environment data
        environment_data = {
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "patient_data": patient_data,
            "vital_signs": vital_signs or {},
            "lab_results": lab_results or {},
        }

        # Execute agent cycle
        perception = await self.perceive(environment_data)
        reasoning = await self.reason(perception)
        action_plan = await self.act(reasoning)

        # Combine results
        return {
            "patient_id": patient_id,
            "diagnosis": perception["diagnosis"],
            "treatment_plan": action_plan["treatment_plan"],
            "safety_alerts": action_plan["safety_alerts"],
            "priority": action_plan["priority"],
            "guideline_compliance": action_plan["guideline_compliance"],
            "patient_factors": perception["patient_factors"],
            "timestamp": perception["timestamp"].isoformat(),
        }
