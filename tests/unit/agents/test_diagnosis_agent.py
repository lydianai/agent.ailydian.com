"""
Unit Tests for Diagnosis Agent

Tests medical imaging analysis and diagnostic reasoning.
"""

import pytest
from datetime import datetime

from agents.diagnosis.agent import (
    DiagnosisAgent,
    ImagingModality,
    BodyRegion,
    DiagnosisConfidence,
    FindingSeverity,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestDiagnosisAgent:
    """Test Diagnosis Agent"""

    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = DiagnosisAgent()

        assert agent is not None
        assert agent.name == "Diagnosis Agent"

    async def test_pneumonia_diagnosis(self):
        """Test pneumonia diagnosis from chest X-ray"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-001",
            imaging_data={
                "modality": ImagingModality.XRAY.value,
                "body_region": BodyRegion.CHEST.value,
                "radiologist_notes": "Right lower lobe consolidation with air bronchogram",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Fever and cough",
                "symptoms": ["fever", "cough", "dyspnea"],
                "vital_signs": {
                    "temperature": 38.5,
                    "heart_rate": 95,
                    "respiratory_rate": 22,
                    "spo2": 94,
                },
            },
            lab_results={
                "wbc": 14.5,
                "crp": 120.0,
            },
        )

        # Should diagnose pneumonia
        assert result["primary_diagnosis"] is not None
        assert "pneumonia" in result["primary_diagnosis"]["diagnosis"]
        assert result["confidence"] > 0.5

        # Should recommend antibiotics
        recommendations_str = " ".join(result["recommendations"]).lower()
        assert "antibiotic" in recommendations_str

    async def test_pulmonary_embolism_diagnosis(self):
        """Test pulmonary embolism diagnosis"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-002",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.CHEST.value,
                "radiologist_notes": "Filling defect in right pulmonary artery",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Sudden onset dyspnea and chest pain",
                "symptoms": ["dyspnea", "chest_pain", "tachycardia"],
                "vital_signs": {
                    "heart_rate": 115,
                    "respiratory_rate": 24,
                    "spo2": 91,
                },
            },
            lab_results={
                "d_dimer": 1200,
            },
        )

        # Should diagnose PE
        assert result["primary_diagnosis"] is not None
        assert "pulmonary_embolism" in result["primary_diagnosis"]["diagnosis"]

        # Should be high risk
        assert result["risk_level"] == "high"

        # Should recommend anticoagulation
        recommendations_str = " ".join(result["recommendations"]).lower()
        assert "anticoagulation" in recommendations_str or "heparin" in recommendations_str

    async def test_myocardial_infarction_diagnosis(self):
        """Test MI diagnosis"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-003",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.CARDIAC.value,
                "radiologist_notes": "Wall motion abnormality anterior wall",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Crushing chest pain",
                "symptoms": ["chest_pain", "dyspnea", "diaphoresis"],
                "vital_signs": {
                    "heart_rate": 105,
                    "systolic_bp": 145,
                },
            },
            lab_results={
                "troponin": 2.5,
            },
        )

        # Should diagnose MI
        assert result["primary_diagnosis"] is not None
        assert "myocardial_infarction" in result["primary_diagnosis"]["diagnosis"]

        # Should be high risk
        assert result["risk_level"] == "high"

        # Should recommend cardiology consultation
        referrals_str = " ".join(result["specialist_referrals"]).lower()
        assert "cardiology" in referrals_str

    async def test_stroke_diagnosis(self):
        """Test ischemic stroke diagnosis"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-004",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.BRAIN.value,
                "radiologist_notes": "Hypodensity in left MCA territory, loss of gray-white differentiation",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Sudden right-sided weakness",
                "symptoms": ["weakness", "speech_difficulty", "facial_droop"],
                "vital_signs": {
                    "heart_rate": 88,
                    "systolic_bp": 165,
                },
            },
        )

        # Should diagnose stroke
        assert result["primary_diagnosis"] is not None
        assert "stroke" in result["primary_diagnosis"]["diagnosis"]

        # Should recommend neurology
        referrals_str = " ".join(result["specialist_referrals"]).lower()
        assert "neurology" in referrals_str

    async def test_appendicitis_diagnosis(self):
        """Test appendicitis diagnosis"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-005",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.ABDOMEN.value,
                "radiologist_notes": "Dilated appendix with periappendiceal fat stranding",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Right lower quadrant pain",
                "symptoms": ["right_lower_quadrant_pain", "nausea", "fever"],
                "vital_signs": {
                    "temperature": 38.2,
                    "heart_rate": 95,
                },
            },
            lab_results={
                "wbc": 15.0,
            },
        )

        # Should diagnose appendicitis
        assert result["primary_diagnosis"] is not None
        assert "appendicitis" in result["primary_diagnosis"]["diagnosis"]

        # Should recommend surgery
        referrals_str = " ".join(result["specialist_referrals"]).lower()
        assert "surgery" in referrals_str


@pytest.mark.unit
@pytest.mark.asyncio
class TestDiagnosticReasoning:
    """Test diagnostic reasoning logic"""

    async def test_differential_diagnosis_generation(self):
        """Test generation of differential diagnosis list"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-006",
            imaging_data={
                "modality": ImagingModality.XRAY.value,
                "body_region": BodyRegion.CHEST.value,
                "radiologist_notes": "Bilateral infiltrates",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Cough and fever",
                "symptoms": ["cough", "fever", "dyspnea"],
                "vital_signs": {"temperature": 38.5},
            },
        )

        # Should have differential diagnosis list
        assert "differential_diagnosis" in result
        assert isinstance(result["differential_diagnosis"], list)

        # Each diagnosis should have required fields
        if len(result["differential_diagnosis"]) > 0:
            dx = result["differential_diagnosis"][0]
            assert "diagnosis" in dx
            assert "confidence_score" in dx
            assert "confidence_level" in dx

    async def test_confidence_levels(self):
        """Test confidence level calculations"""
        agent = DiagnosisAgent()

        # High confidence case (clear pneumonia)
        result = await agent.analyze_case(
            patient_id="TEST-007",
            imaging_data={
                "modality": ImagingModality.XRAY.value,
                "body_region": BodyRegion.CHEST.value,
                "radiologist_notes": "Consolidation with air bronchogram and pleural effusion",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "symptoms": ["fever", "cough", "dyspnea", "chest_pain"],
                "vital_signs": {"temperature": 39.0},
            },
            lab_results={"wbc": 16.0, "crp": 150.0},
        )

        # Should have high confidence
        assert result["confidence"] > 0.6

    async def test_critical_findings_detection(self):
        """Test detection of critical findings"""
        agent = DiagnosisAgent()

        result = await agent.analyze_case(
            patient_id="TEST-008",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.BRAIN.value,
                "radiologist_notes": "Large intracranial hemorrhage",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "chief_complaint": "Severe headache and altered mental status",
                "symptoms": ["severe_headache", "altered_mental_status"],
                "vital_signs": {"systolic_bp": 185},
            },
        )

        # Should detect critical finding
        assert len(result["critical_findings"]) > 0

    async def test_risk_stratification(self):
        """Test risk level assessment"""
        agent = DiagnosisAgent()

        # High-risk case (PE)
        high_risk_result = await agent.analyze_case(
            patient_id="TEST-009",
            imaging_data={
                "modality": ImagingModality.CT.value,
                "body_region": BodyRegion.CHEST.value,
                "radiologist_notes": "Bilateral pulmonary emboli",
                "study_date": datetime.utcnow(),
            },
            clinical_data={
                "symptoms": ["dyspnea", "chest_pain"],
                "vital_signs": {"spo2": 88},
            },
            lab_results={"d_dimer": 2000},
        )

        # Should be high risk
        assert high_risk_result["risk_level"] == "high"


@pytest.mark.unit
class TestImagingAnalysis:
    """Test imaging analysis functions"""

    def test_parse_radiologist_notes(self):
        """Test parsing of radiologist notes"""
        agent = DiagnosisAgent()

        notes = "Consolidation in right lower lobe with pleural effusion"
        findings = agent._parse_radiologist_notes(notes)

        # Should detect consolidation and effusion
        finding_types = [f["finding"] for f in findings]
        assert "consolidation" in finding_types
        assert "effusion" in finding_types

    def test_vital_sign_abnormality_detection(self):
        """Test vital sign abnormality detection"""
        agent = DiagnosisAgent()

        vital_signs = {
            "temperature": 39.0,
            "heart_rate": 115,
            "respiratory_rate": 28,
            "spo2": 88,
        }

        abnormalities = agent._assess_vital_abnormalities(vital_signs)

        assert "fever" in abnormalities
        assert "tachycardia" in abnormalities
        assert "tachypnea" in abnormalities
        assert "hypoxia" in abnormalities
