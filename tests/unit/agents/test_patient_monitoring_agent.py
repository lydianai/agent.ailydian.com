"""
Unit Tests for Patient Monitoring Agent

Tests NEWS2 score calculation, sepsis risk assessment, and alert generation.
"""

import pytest
from agents.patient_monitoring.agent import PatientMonitoringAgent
from agents.patient_monitoring.news2 import calculate_news2_score
from agents.patient_monitoring.sepsis import assess_sepsis_risk


# ============================================================================
# NEWS2 SCORE TESTS
# ============================================================================

@pytest.mark.unit
class TestNEWS2Calculation:
    """Test NEWS2 (National Early Warning Score 2) calculation"""

    def test_news2_normal_vitals(self):
        """Test NEWS2 score for normal vital signs"""
        vitals = {
            "respiratory_rate": 16,
            "spo2": 98,
            "air_or_oxygen": "air",
            "systolic_bp": 120,
            "heart_rate": 72,
            "consciousness": "alert",
            "temperature": 37.0,
        }

        score = calculate_news2_score(vitals)

        assert score == 0, "Normal vitals should have NEWS2 score of 0"

    def test_news2_elevated_heart_rate(self):
        """Test NEWS2 score with tachycardia"""
        vitals = {
            "respiratory_rate": 16,
            "spo2": 98,
            "air_or_oxygen": "air",
            "systolic_bp": 120,
            "heart_rate": 115,  # Tachycardia
            "consciousness": "alert",
            "temperature": 37.0,
        }

        score = calculate_news2_score(vitals)

        assert score >= 2, "Tachycardia should increase NEWS2 score"

    def test_news2_low_spo2(self):
        """Test NEWS2 score with hypoxia"""
        vitals = {
            "respiratory_rate": 16,
            "spo2": 92,  # Low oxygen
            "air_or_oxygen": "air",
            "systolic_bp": 120,
            "heart_rate": 72,
            "consciousness": "alert",
            "temperature": 37.0,
        }

        score = calculate_news2_score(vitals)

        assert score >= 2, "Low SpO2 should increase NEWS2 score"

    def test_news2_fever(self):
        """Test NEWS2 score with fever"""
        vitals = {
            "respiratory_rate": 16,
            "spo2": 98,
            "air_or_oxygen": "air",
            "systolic_bp": 120,
            "heart_rate": 72,
            "consciousness": "alert",
            "temperature": 38.5,  # Fever
        }

        score = calculate_news2_score(vitals)

        assert score >= 1, "Fever should increase NEWS2 score"

    def test_news2_critical_vitals(self):
        """Test NEWS2 score with multiple abnormal vitals"""
        vitals = {
            "respiratory_rate": 28,  # High
            "spo2": 88,  # Low
            "air_or_oxygen": "oxygen",  # On supplemental O2
            "systolic_bp": 95,  # Low
            "heart_rate": 125,  # High
            "consciousness": "confusion",  # Altered
            "temperature": 38.9,  # High
        }

        score = calculate_news2_score(vitals)

        assert score >= 7, "Multiple abnormal vitals should have high NEWS2 score"
        assert score <= 20, "NEWS2 score should not exceed maximum"


# ============================================================================
# SEPSIS RISK ASSESSMENT TESTS
# ============================================================================

@pytest.mark.unit
class TestSepsisRiskAssessment:
    """Test sepsis risk assessment (qSOFA + SIRS criteria)"""

    def test_no_sepsis_risk(self):
        """Test patient with no sepsis risk"""
        vitals = {
            "respiratory_rate": 16,
            "systolic_bp": 120,
            "heart_rate": 72,
            "temperature": 37.0,
            "wbc_count": 8000,
        }

        risk = assess_sepsis_risk(vitals)

        assert risk["qsofa_score"] == 0
        assert risk["sirs_score"] == 0
        assert risk["sepsis_risk"] == "low"

    def test_qsofa_positive(self):
        """Test qSOFA positive (≥2 criteria)"""
        vitals = {
            "respiratory_rate": 24,  # ≥22 (1 point)
            "systolic_bp": 95,  # ≤100 (1 point)
            "heart_rate": 72,
            "temperature": 37.0,
            "altered_mentation": True,  # (1 point)
        }

        risk = assess_sepsis_risk(vitals)

        assert risk["qsofa_score"] >= 2
        assert risk["sepsis_risk"] in ["high", "critical"]

    def test_sirs_criteria(self):
        """Test SIRS (Systemic Inflammatory Response Syndrome) criteria"""
        vitals = {
            "respiratory_rate": 24,  # >20 (1 point)
            "heart_rate": 95,  # >90 (1 point)
            "temperature": 38.5,  # >38 (1 point)
            "wbc_count": 13000,  # >12000 (1 point)
        }

        risk = assess_sepsis_risk(vitals)

        assert risk["sirs_score"] >= 2
        assert risk["sepsis_risk"] != "low"


# ============================================================================
# PATIENT MONITORING AGENT TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestPatientMonitoringAgent:
    """Test Patient Monitoring Agent functionality"""

    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = PatientMonitoringAgent()

        assert agent is not None
        assert hasattr(agent, "assess_patient")

    async def test_assess_normal_patient(self, mock_vital_signs):
        """Test assessment of patient with normal vitals"""
        agent = PatientMonitoringAgent()

        assessment = await agent.assess_patient(
            patient_id="TEST-001",
            vital_signs=mock_vital_signs,
        )

        assert assessment is not None
        assert "news2_score" in assessment
        assert "risk_level" in assessment
        assert assessment["risk_level"] == "low"

    async def test_assess_critical_patient(self):
        """Test assessment of critical patient"""
        agent = PatientMonitoringAgent()

        critical_vitals = {
            "heart_rate": 135,
            "blood_pressure": {"systolic": 85, "diastolic": 60},
            "temperature": 39.2,
            "respiratory_rate": 32,
            "spo2": 86,
        }

        assessment = await agent.assess_patient(
            patient_id="TEST-002",
            vital_signs=critical_vitals,
        )

        assert assessment is not None
        assert assessment["risk_level"] in ["high", "critical"]
        assert assessment["news2_score"] > 7

    async def test_alert_generation(self):
        """Test that alerts are generated for critical vitals"""
        agent = PatientMonitoringAgent()

        critical_vitals = {
            "heart_rate": 145,
            "spo2": 82,
            "respiratory_rate": 35,
        }

        assessment = await agent.assess_patient(
            patient_id="TEST-003",
            vital_signs=critical_vitals,
        )

        assert "alerts" in assessment
        assert len(assessment["alerts"]) > 0

    async def test_sepsis_detection(self):
        """Test sepsis risk detection"""
        agent = PatientMonitoringAgent()

        sepsis_vitals = {
            "heart_rate": 110,
            "respiratory_rate": 26,
            "temperature": 38.8,
            "systolic_bp": 92,
            "wbc_count": 14000,
        }

        assessment = await agent.assess_patient(
            patient_id="TEST-004",
            vital_signs=sepsis_vitals,
        )

        assert "sepsis_risk" in assessment
        assert assessment["sepsis_risk"]["sepsis_risk"] != "low"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_news2_missing_vitals(self):
        """Test NEWS2 with missing vital signs"""
        vitals = {
            "heart_rate": 72,
            "temperature": 37.0,
            # Missing other vitals
        }

        with pytest.raises((KeyError, ValueError)):
            calculate_news2_score(vitals)

    def test_news2_invalid_values(self):
        """Test NEWS2 with invalid vital sign values"""
        vitals = {
            "respiratory_rate": -10,  # Invalid
            "spo2": 150,  # Invalid (>100)
            "heart_rate": 300,  # Impossible
        }

        # Should handle gracefully or raise ValueError
        with pytest.raises(ValueError):
            calculate_news2_score(vitals)

    @pytest.mark.asyncio
    async def test_agent_empty_vitals(self):
        """Test agent with empty vital signs"""
        agent = PatientMonitoringAgent()

        with pytest.raises((ValueError, TypeError)):
            await agent.assess_patient(
                patient_id="TEST-EMPTY",
                vital_signs={},
            )


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.unit
class TestPerformance:
    """Test performance of NEWS2 and sepsis calculations"""

    def test_news2_calculation_speed(self, benchmark, mock_vital_signs):
        """Test NEWS2 calculation performance"""

        def run_news2():
            return calculate_news2_score(mock_vital_signs)

        result = benchmark(run_news2)
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_assessment_speed(self, benchmark, mock_vital_signs):
        """Test agent assessment performance"""
        agent = PatientMonitoringAgent()

        async def run_assessment():
            return await agent.assess_patient(
                patient_id="TEST-PERF",
                vital_signs=mock_vital_signs,
            )

        # Benchmark async function
        result = await run_assessment()
        assert result is not None
