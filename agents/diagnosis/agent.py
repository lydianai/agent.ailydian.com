"""
Diagnosis Agent - Medical Imaging & Clinical Diagnosis

Provides AI-powered diagnostic support using:
- MONAI: Medical image analysis (CT, MRI, X-Ray)
- Clinical reasoning: Differential diagnosis generation
- Evidence-based medicine: Guidelines and recommendations
- Risk stratification: Disease probability scoring
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import base64
import io

from agents.base_agent import BaseAgent, AgentCapability
from core.logging import get_logger
from core.monitoring.metrics import track_agent_performance

logger = get_logger(__name__)


class ImagingModality(str, Enum):
    """Medical imaging modalities"""
    XRAY = "xray"
    CT = "ct"
    MRI = "mri"
    ULTRASOUND = "ultrasound"
    MAMMOGRAPHY = "mammography"
    PET = "pet"


class BodyRegion(str, Enum):
    """Body regions for imaging"""
    CHEST = "chest"
    ABDOMEN = "abdomen"
    BRAIN = "brain"
    SPINE = "spine"
    PELVIS = "pelvis"
    EXTREMITIES = "extremities"
    CARDIAC = "cardiac"


class DiagnosisConfidence(str, Enum):
    """Confidence levels for diagnosis"""
    DEFINITE = "definite"  # >90%
    PROBABLE = "probable"  # 70-90%
    POSSIBLE = "possible"  # 40-70%
    UNLIKELY = "unlikely"  # <40%


class FindingSeverity(str, Enum):
    """Severity of imaging findings"""
    CRITICAL = "critical"  # Life-threatening
    SEVERE = "severe"  # Requires urgent intervention
    MODERATE = "moderate"  # Requires timely intervention
    MILD = "mild"  # Monitor or routine followup
    INCIDENTAL = "incidental"  # Unrelated finding


class DiagnosisAgent(BaseAgent):
    """
    Diagnosis Agent - AI-Powered Diagnostic Support

    Capabilities:
    - Medical image analysis (MONAI framework)
    - Differential diagnosis generation
    - Clinical reasoning and evidence synthesis
    - Risk stratification
    - Treatment recommendation suggestions
    """

    def __init__(self):
        super().__init__(
            agent_id="diagnosis-agent",
            name="Diagnosis Agent",
            capabilities=[
                AgentCapability.MEDICAL_IMAGING,
                AgentCapability.DIFFERENTIAL_DIAGNOSIS,
                AgentCapability.CLINICAL_REASONING,
            ],
        )

        # Common pathology patterns (simplified for demo)
        self.pathology_patterns = {
            "pneumonia": {
                "imaging_features": ["consolidation", "air_bronchogram", "pleural_effusion"],
                "clinical_features": ["fever", "cough", "dyspnea", "chest_pain"],
                "labs": ["elevated_wbc", "elevated_crp"],
            },
            "pulmonary_embolism": {
                "imaging_features": ["filling_defect", "dilated_pulmonary_artery"],
                "clinical_features": ["dyspnea", "chest_pain", "tachycardia"],
                "labs": ["elevated_d_dimer"],
            },
            "stroke_ischemic": {
                "imaging_features": ["hypodensity", "loss_of_gray_white_differentiation"],
                "clinical_features": ["weakness", "speech_difficulty", "facial_droop"],
                "labs": ["normal_initially"],
            },
            "myocardial_infarction": {
                "imaging_features": ["wall_motion_abnormality", "perfusion_defect"],
                "clinical_features": ["chest_pain", "dyspnea", "diaphoresis"],
                "labs": ["elevated_troponin", "elevated_ck_mb"],
            },
            "appendicitis": {
                "imaging_features": ["dilated_appendix", "periappendiceal_fat_stranding"],
                "clinical_features": ["right_lower_quadrant_pain", "nausea", "fever"],
                "labs": ["elevated_wbc"],
            },
        }

    async def perceive(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive diagnostic data

        Args:
            environment_data: {
                "patient_id": str,
                "imaging_data": {
                    "modality": str,
                    "body_region": str,
                    "image_data": bytes or str (base64),
                    "study_date": datetime,
                    "radiologist_notes": str (optional),
                },
                "clinical_data": {
                    "chief_complaint": str,
                    "symptoms": list,
                    "vital_signs": dict,
                    "medical_history": list,
                    "medications": list,
                    "allergies": list,
                },
                "lab_results": dict (optional),
            }

        Returns:
            Processed diagnostic perception
        """
        patient_id = environment_data.get("patient_id")
        imaging_data = environment_data.get("imaging_data", {})
        clinical_data = environment_data.get("clinical_data", {})
        lab_results = environment_data.get("lab_results", {})

        # Extract imaging features
        imaging_features = await self._analyze_imaging(imaging_data)

        # Extract clinical features
        clinical_features = self._extract_clinical_features(clinical_data)

        # Extract lab features
        lab_features = self._extract_lab_features(lab_results)

        return {
            "patient_id": patient_id,
            "imaging_features": imaging_features,
            "clinical_features": clinical_features,
            "lab_features": lab_features,
            "timestamp": datetime.utcnow(),
        }

    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about diagnosis

        Returns:
            Differential diagnosis with confidence scores
        """
        imaging_features = perception["imaging_features"]
        clinical_features = perception["clinical_features"]
        lab_features = perception["lab_features"]

        # Generate differential diagnosis
        differential = await self._generate_differential_diagnosis(
            imaging_features, clinical_features, lab_features
        )

        # Risk stratification
        risk_assessment = self._assess_risk(differential, clinical_features)

        # Identify critical findings
        critical_findings = self._identify_critical_findings(
            imaging_features, differential
        )

        # Calculate overall confidence
        confidence = self._calculate_diagnostic_confidence(differential)

        return {
            "differential_diagnosis": differential,
            "risk_assessment": risk_assessment,
            "critical_findings": critical_findings,
            "confidence": confidence,
        }

    async def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate diagnostic action plan

        Returns:
            Recommendations and next steps
        """
        differential = reasoning["differential_diagnosis"]
        risk_assessment = reasoning["risk_assessment"]
        critical_findings = reasoning["critical_findings"]

        # Prioritized recommendations
        recommendations = self._generate_recommendations(
            differential, risk_assessment, critical_findings
        )

        # Additional testing needed
        additional_tests = self._recommend_additional_tests(differential)

        # Specialist referrals
        referrals = self._recommend_referrals(differential, risk_assessment)

        # Follow-up plan
        followup_plan = self._create_followup_plan(differential, risk_assessment)

        return {
            "primary_diagnosis": differential[0] if differential else None,
            "differential_diagnosis": differential,
            "recommendations": recommendations,
            "additional_tests": additional_tests,
            "specialist_referrals": referrals,
            "followup_plan": followup_plan,
            "critical_findings": critical_findings,
            "risk_level": risk_assessment["overall_risk"],
        }

    # ========================================================================
    # IMAGE ANALYSIS
    # ========================================================================

    async def _analyze_imaging(self, imaging_data: dict) -> Dict[str, Any]:
        """
        Analyze medical imaging (simulated MONAI processing)

        In production, this would use MONAI models for:
        - Image segmentation
        - Lesion detection
        - Anatomical landmark identification
        - Abnormality classification
        """
        modality = imaging_data.get("modality", "")
        body_region = imaging_data.get("body_region", "")
        radiologist_notes = imaging_data.get("radiologist_notes", "")

        # Simulated findings (in production, use MONAI)
        findings = []

        # Parse radiologist notes for findings
        if radiologist_notes:
            findings.extend(self._parse_radiologist_notes(radiologist_notes))

        # Simulated imaging findings based on modality/region
        if modality == ImagingModality.XRAY and body_region == BodyRegion.CHEST:
            # Common chest X-ray findings
            simulated_findings = self._simulate_chest_xray_analysis()
            findings.extend(simulated_findings)

        elif modality == ImagingModality.CT and body_region == BodyRegion.BRAIN:
            # Common brain CT findings
            simulated_findings = self._simulate_brain_ct_analysis()
            findings.extend(simulated_findings)

        return {
            "modality": modality,
            "body_region": body_region,
            "findings": findings,
            "quality": "diagnostic",  # Image quality assessment
        }

    def _parse_radiologist_notes(self, notes: str) -> List[Dict]:
        """Parse radiologist notes to extract findings"""
        findings = []

        # Simple keyword detection (in production, use NLP)
        keywords = {
            "consolidation": {"severity": FindingSeverity.MODERATE, "location": "lung"},
            "nodule": {"severity": FindingSeverity.MODERATE, "location": "lung"},
            "mass": {"severity": FindingSeverity.SEVERE, "location": "varies"},
            "effusion": {"severity": FindingSeverity.MODERATE, "location": "pleural"},
            "fracture": {"severity": FindingSeverity.SEVERE, "location": "bone"},
            "hemorrhage": {"severity": FindingSeverity.CRITICAL, "location": "brain"},
            "infarct": {"severity": FindingSeverity.CRITICAL, "location": "brain"},
        }

        notes_lower = notes.lower()

        for keyword, details in keywords.items():
            if keyword in notes_lower:
                findings.append({
                    "finding": keyword,
                    "severity": details["severity"].value,
                    "location": details["location"],
                    "source": "radiologist_report",
                })

        return findings

    def _simulate_chest_xray_analysis(self) -> List[Dict]:
        """Simulate chest X-ray analysis (placeholder for MONAI)"""
        # In production, this would be MONAI model inference
        return []

    def _simulate_brain_ct_analysis(self) -> List[Dict]:
        """Simulate brain CT analysis (placeholder for MONAI)"""
        # In production, this would be MONAI model inference
        return []

    # ========================================================================
    # CLINICAL FEATURE EXTRACTION
    # ========================================================================

    def _extract_clinical_features(self, clinical_data: dict) -> List[str]:
        """Extract relevant clinical features"""
        features = []

        # Symptoms
        symptoms = clinical_data.get("symptoms", [])
        features.extend(symptoms)

        # Chief complaint
        complaint = clinical_data.get("chief_complaint", "")
        if complaint:
            features.append(complaint)

        # Vital signs abnormalities
        vital_signs = clinical_data.get("vital_signs", {})
        vital_features = self._assess_vital_abnormalities(vital_signs)
        features.extend(vital_features)

        return features

    def _assess_vital_abnormalities(self, vital_signs: dict) -> List[str]:
        """Assess vital sign abnormalities"""
        abnormalities = []

        # Temperature
        temp = vital_signs.get("temperature", 37.0)
        if temp >= 38.0:
            abnormalities.append("fever")
        elif temp <= 35.0:
            abnormalities.append("hypothermia")

        # Heart rate
        hr = vital_signs.get("heart_rate", 75)
        if hr > 100:
            abnormalities.append("tachycardia")
        elif hr < 60:
            abnormalities.append("bradycardia")

        # Respiratory rate
        rr = vital_signs.get("respiratory_rate", 16)
        if rr > 20:
            abnormalities.append("tachypnea")

        # Blood pressure
        sbp = vital_signs.get("systolic_bp", 120)
        if sbp > 140:
            abnormalities.append("hypertension")
        elif sbp < 90:
            abnormalities.append("hypotension")

        # Oxygen saturation
        spo2 = vital_signs.get("spo2", 98)
        if spo2 < 94:
            abnormalities.append("hypoxia")

        return abnormalities

    def _extract_lab_features(self, lab_results: dict) -> List[str]:
        """Extract relevant lab features"""
        features = []

        # WBC
        wbc = lab_results.get("wbc")
        if wbc and wbc > 11.0:
            features.append("elevated_wbc")

        # CRP
        crp = lab_results.get("crp")
        if crp and crp > 10.0:
            features.append("elevated_crp")

        # D-dimer
        d_dimer = lab_results.get("d_dimer")
        if d_dimer and d_dimer > 500:
            features.append("elevated_d_dimer")

        # Troponin
        troponin = lab_results.get("troponin")
        if troponin and troponin > 0.04:
            features.append("elevated_troponin")

        return features

    # ========================================================================
    # DIFFERENTIAL DIAGNOSIS
    # ========================================================================

    async def _generate_differential_diagnosis(
        self,
        imaging_features: dict,
        clinical_features: list,
        lab_features: list,
    ) -> List[Dict]:
        """
        Generate differential diagnosis with confidence scores

        Returns:
            List of diagnoses sorted by likelihood
        """
        candidates = []

        # Score each pathology
        for pathology, patterns in self.pathology_patterns.items():
            score = self._calculate_pathology_score(
                pathology, patterns, imaging_features, clinical_features, lab_features
            )

            if score > 0:
                candidates.append({
                    "diagnosis": pathology,
                    "confidence_score": score,
                    "confidence_level": self._score_to_confidence_level(score),
                    "supporting_evidence": self._get_supporting_evidence(
                        patterns, imaging_features, clinical_features, lab_features
                    ),
                })

        # Sort by score
        candidates.sort(key=lambda x: x["confidence_score"], reverse=True)

        return candidates[:5]  # Top 5 differential diagnoses

    def _calculate_pathology_score(
        self,
        pathology: str,
        patterns: dict,
        imaging_features: dict,
        clinical_features: list,
        lab_features: list,
    ) -> float:
        """Calculate likelihood score for a pathology"""
        score = 0.0

        # Imaging features (weight: 40%)
        imaging_findings = [f["finding"] for f in imaging_features.get("findings", [])]
        for expected_feature in patterns.get("imaging_features", []):
            if expected_feature in imaging_findings:
                score += 0.4 / len(patterns["imaging_features"])

        # Clinical features (weight: 40%)
        for expected_feature in patterns.get("clinical_features", []):
            if expected_feature in clinical_features:
                score += 0.4 / len(patterns["clinical_features"])

        # Lab features (weight: 20%)
        for expected_lab in patterns.get("labs", []):
            if expected_lab in lab_features:
                score += 0.2 / len(patterns["labs"])

        return min(score, 1.0)

    def _score_to_confidence_level(self, score: float) -> str:
        """Convert numeric score to confidence level"""
        if score >= 0.9:
            return DiagnosisConfidence.DEFINITE.value
        elif score >= 0.7:
            return DiagnosisConfidence.PROBABLE.value
        elif score >= 0.4:
            return DiagnosisConfidence.POSSIBLE.value
        else:
            return DiagnosisConfidence.UNLIKELY.value

    def _get_supporting_evidence(
        self, patterns: dict, imaging_features: dict, clinical_features: list, lab_features: list
    ) -> List[str]:
        """Get supporting evidence for diagnosis"""
        evidence = []

        # Imaging evidence
        imaging_findings = [f["finding"] for f in imaging_features.get("findings", [])]
        for feature in patterns.get("imaging_features", []):
            if feature in imaging_findings:
                evidence.append(f"Imaging: {feature}")

        # Clinical evidence
        for feature in patterns.get("clinical_features", []):
            if feature in clinical_features:
                evidence.append(f"Clinical: {feature}")

        # Lab evidence
        for feature in patterns.get("labs", []):
            if feature in lab_features:
                evidence.append(f"Lab: {feature}")

        return evidence

    # ========================================================================
    # RISK ASSESSMENT
    # ========================================================================

    def _assess_risk(self, differential: List[Dict], clinical_features: list) -> Dict:
        """Assess patient risk based on diagnosis"""
        if not differential:
            return {"overall_risk": "low", "risk_factors": []}

        primary_diagnosis = differential[0]
        diagnosis_name = primary_diagnosis["diagnosis"]

        # High-risk conditions
        high_risk_conditions = [
            "pulmonary_embolism",
            "myocardial_infarction",
            "stroke_ischemic",
            "hemorrhage",
        ]

        if diagnosis_name in high_risk_conditions:
            risk_level = "high"
        elif primary_diagnosis["confidence_score"] > 0.7:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return {
            "overall_risk": risk_level,
            "risk_factors": self._identify_risk_factors(clinical_features),
        }

    def _identify_risk_factors(self, clinical_features: list) -> List[str]:
        """Identify risk factors from clinical features"""
        risk_factors = []

        risk_map = {
            "hypertension": "Cardiovascular risk",
            "hypoxia": "Respiratory compromise",
            "tachycardia": "Hemodynamic instability",
            "fever": "Infectious process",
        }

        for feature in clinical_features:
            if feature in risk_map:
                risk_factors.append(risk_map[feature])

        return risk_factors

    def _identify_critical_findings(
        self, imaging_features: dict, differential: List[Dict]
    ) -> List[Dict]:
        """Identify critical findings requiring immediate action"""
        critical = []

        # Critical imaging findings
        for finding in imaging_features.get("findings", []):
            if finding.get("severity") == FindingSeverity.CRITICAL.value:
                critical.append({
                    "type": "imaging",
                    "finding": finding["finding"],
                    "action_required": "Immediate specialist consultation",
                })

        # Critical diagnoses
        for dx in differential:
            if dx["diagnosis"] in ["pulmonary_embolism", "myocardial_infarction"]:
                if dx["confidence_score"] > 0.6:
                    critical.append({
                        "type": "diagnosis",
                        "finding": dx["diagnosis"],
                        "action_required": "Immediate treatment protocol activation",
                    })

        return critical

    def _calculate_diagnostic_confidence(self, differential: List[Dict]) -> float:
        """Calculate overall diagnostic confidence"""
        if not differential:
            return 0.0

        # Highest confidence diagnosis
        return differential[0]["confidence_score"]

    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================

    def _generate_recommendations(
        self, differential: List[Dict], risk_assessment: dict, critical_findings: list
    ) -> List[str]:
        """Generate treatment and management recommendations"""
        recommendations = []

        if not differential:
            recommendations.append("Insufficient data for specific recommendations")
            return recommendations

        primary_dx = differential[0]
        diagnosis = primary_dx["diagnosis"]

        # Diagnosis-specific recommendations
        if diagnosis == "pneumonia":
            recommendations.extend([
                "Empiric antibiotic therapy (e.g., Ceftriaxone + Azithromycin)",
                "Oxygen therapy if SpO2 < 94%",
                "IV fluids for hydration",
                "Repeat chest X-ray in 48-72 hours",
            ])

        elif diagnosis == "pulmonary_embolism":
            recommendations.extend([
                "Immediate anticoagulation (Heparin or LMWH)",
                "Consider thrombolysis if massive PE",
                "Oxygen therapy",
                "Hemodynamic monitoring",
            ])

        elif diagnosis == "myocardial_infarction":
            recommendations.extend([
                "Aspirin 325mg stat",
                "Clopidogrel loading dose",
                "Heparin anticoagulation",
                "Emergent cardiology consultation for PCI",
            ])

        # Critical findings
        if critical_findings:
            recommendations.insert(0, "CRITICAL: Address life-threatening findings immediately")

        return recommendations

    def _recommend_additional_tests(self, differential: List[Dict]) -> List[str]:
        """Recommend additional diagnostic tests"""
        if not differential:
            return []

        tests = []
        primary_dx = differential[0]["diagnosis"]

        test_map = {
            "pneumonia": ["Blood cultures", "Sputum culture", "Complete blood count"],
            "pulmonary_embolism": ["CT pulmonary angiography", "D-dimer", "ECG", "Arterial blood gas"],
            "myocardial_infarction": ["Serial troponins", "ECG", "Coronary angiography"],
            "appendicitis": ["CT abdomen/pelvis with contrast", "Complete blood count"],
        }

        return test_map.get(primary_dx, [])

    def _recommend_referrals(self, differential: List[Dict], risk_assessment: dict) -> List[str]:
        """Recommend specialist referrals"""
        if not differential:
            return []

        referrals = []
        primary_dx = differential[0]["diagnosis"]

        referral_map = {
            "pulmonary_embolism": ["Pulmonology", "Cardiology"],
            "myocardial_infarction": ["Cardiology (URGENT)"],
            "stroke_ischemic": ["Neurology (URGENT)"],
            "appendicitis": ["General Surgery"],
        }

        referrals = referral_map.get(primary_dx, [])

        if risk_assessment["overall_risk"] == "high":
            referrals.insert(0, "Critical Care/ICU consultation")

        return referrals

    def _create_followup_plan(self, differential: List[Dict], risk_assessment: dict) -> Dict:
        """Create follow-up care plan"""
        if not differential:
            return {"timeline": "As needed", "monitoring": []}

        risk_level = risk_assessment["overall_risk"]

        if risk_level == "high":
            timeline = "24-48 hours or sooner if worsening"
            monitoring = ["Vital signs q4h", "Repeat imaging in 24-48h", "Daily labs"]

        elif risk_level == "moderate":
            timeline = "1 week"
            monitoring = ["Vital signs daily", "Repeat imaging in 1 week", "Symptom monitoring"]

        else:
            timeline = "2-4 weeks"
            monitoring = ["Symptom diary", "Repeat imaging as needed"]

        return {
            "timeline": timeline,
            "monitoring": monitoring,
        }

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    @track_agent_performance("Diagnosis Agent")
    async def analyze_case(
        self,
        patient_id: str,
        imaging_data: dict,
        clinical_data: dict,
        lab_results: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive diagnostic analysis

        Args:
            patient_id: Patient identifier
            imaging_data: Medical imaging data
            clinical_data: Clinical presentation
            lab_results: Laboratory results (optional)

        Returns:
            Complete diagnostic assessment with recommendations
        """
        # Build environment data
        environment_data = {
            "patient_id": patient_id,
            "imaging_data": imaging_data,
            "clinical_data": clinical_data,
            "lab_results": lab_results or {},
        }

        # Execute agent cycle
        perception = await self.perceive(environment_data)
        reasoning = await self.reason(perception)
        action_plan = await self.act(reasoning)

        # Combine results
        return {
            "patient_id": patient_id,
            "primary_diagnosis": action_plan["primary_diagnosis"],
            "differential_diagnosis": action_plan["differential_diagnosis"],
            "confidence": reasoning["confidence"],
            "risk_level": action_plan["risk_level"],
            "critical_findings": action_plan["critical_findings"],
            "recommendations": action_plan["recommendations"],
            "additional_tests": action_plan["additional_tests"],
            "specialist_referrals": action_plan["specialist_referrals"],
            "followup_plan": action_plan["followup_plan"],
            "imaging_findings": perception["imaging_features"]["findings"],
            "timestamp": perception["timestamp"].isoformat(),
        }
