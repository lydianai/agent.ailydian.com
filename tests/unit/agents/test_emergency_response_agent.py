"""
Unit Tests for Emergency Response Agent

Tests ESI triage, ABCDE assessment, and protocol activation.
"""

import pytest
from datetime import datetime

from agents.emergency_response.agent import (
    EmergencyResponseAgent,
    TriageLevel,
    EmergencyType,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestEmergencyResponseAgent:
    """Test Emergency Response Agent"""

    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = EmergencyResponseAgent()

        assert agent is not None
        assert agent.name == "Emergency Response Agent"

    async def test_triage_level_1_cardiac_arrest(self):
        """Test ESI Level 1 for cardiac arrest"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Unresponsive, no pulse",
            vital_signs={
                "heart_rate": 0,
                "respiratory_rate": 0,
                "systolic_bp": 0,
                "spo2": 0,
            },
            symptoms=["unresponsive", "no_pulse"],
        )

        assert result["triage_level"] == TriageLevel.LEVEL_1.value
        assert result["priority"] == "CRITICAL"
        assert "CPR" in str(result["action_plan"]["immediate_actions"])

    async def test_triage_level_2_stroke(self):
        """Test ESI Level 2 for stroke symptoms"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Sudden weakness on right side",
            vital_signs={
                "heart_rate": 88,
                "respiratory_rate": 18,
                "systolic_bp": 165,
                "spo2": 96,
            },
            symptoms=["facial droop", "arm weakness", "speech difficulty"],
        )

        assert result["triage_level"] == TriageLevel.LEVEL_2.value
        assert result["emergency_type"] == EmergencyType.STROKE.value
        assert len(result["protocols_activated"]) > 0
        assert any("Stroke Alert" in p["protocol"] for p in result["protocols_activated"])

    async def test_triage_level_3_stable_multiple_resources(self):
        """Test ESI Level 3 for stable patient needing multiple resources"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Abdominal pain and fever",
            vital_signs={
                "heart_rate": 95,
                "respiratory_rate": 18,
                "systolic_bp": 125,
                "spo2": 97,
                "temperature": 38.5,
            },
            symptoms=["abdominal pain", "nausea", "fever"],
        )

        # Should be level 3 (stable but needs labs + imaging)
        assert result["triage_level"] in [
            TriageLevel.LEVEL_3.value,
            TriageLevel.LEVEL_2.value,
        ]

    async def test_triage_level_5_minor_complaint(self):
        """Test ESI Level 5 for minor complaint"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Minor cut on finger",
            vital_signs={
                "heart_rate": 72,
                "respiratory_rate": 16,
                "systolic_bp": 120,
                "spo2": 98,
            },
            symptoms=["small laceration"],
        )

        assert result["triage_level"] in [
            TriageLevel.LEVEL_4.value,
            TriageLevel.LEVEL_5.value,
        ]

    async def test_chest_pain_protocol_activation(self):
        """Test STEMI protocol activation for chest pain"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Crushing chest pain radiating to left arm",
            vital_signs={
                "heart_rate": 110,
                "respiratory_rate": 22,
                "systolic_bp": 145,
                "spo2": 95,
            },
            symptoms=["chest pain", "diaphoresis", "nausea"],
        )

        assert result["emergency_type"] == EmergencyType.CHEST_PAIN.value
        assert len(result["protocols_activated"]) > 0
        assert any("STEMI" in p["protocol"] for p in result["protocols_activated"])

    async def test_red_flag_detection(self):
        """Test red flag detection"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Severe headache with confusion",
            vital_signs={
                "heart_rate": 115,
                "respiratory_rate": 20,
                "systolic_bp": 185,
                "spo2": 97,
            },
            symptoms=["severe headache", "confusion", "nausea"],
        )

        assert "altered_mental_status" in result["red_flags"]
        assert result["triage_level"] == TriageLevel.LEVEL_2.value

    async def test_abcde_assessment(self):
        """Test ABCDE primary survey"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Difficulty breathing after bee sting",
            vital_signs={
                "heart_rate": 130,
                "respiratory_rate": 32,
                "systolic_bp": 85,
                "spo2": 88,
            },
            symptoms=["stridor", "hives", "respiratory distress"],
        )

        abcde = result["abcde_assessment"]

        # Airway compromised (stridor)
        assert abcde["airway"]["status"] == "compromised"

        # Breathing inadequate (RR 32, SpO2 88)
        assert abcde["breathing"]["status"] == "inadequate"

        # Circulation compromised (SBP 85, HR 130)
        assert abcde["circulation"]["status"] == "compromised"

        # Should activate anaphylaxis interventions
        assert any("Epinephrine" in str(action) for action in result["action_plan"]["immediate_actions"])


@pytest.mark.unit
class TestTriageLevelCalculations:
    """Test specific triage level calculations"""

    @pytest.mark.asyncio
    async def test_hypotension_triggers_level_1(self):
        """Test severe hypotension triggers Level 1"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Weakness and dizziness",
            vital_signs={
                "heart_rate": 145,
                "respiratory_rate": 28,
                "systolic_bp": 65,  # Severe hypotension
                "spo2": 92,
            },
            symptoms=["weakness", "dizziness"],
        )

        assert result["triage_level"] == TriageLevel.LEVEL_1.value

    @pytest.mark.asyncio
    async def test_severe_hypoxia_triggers_level_1(self):
        """Test severe hypoxia triggers Level 1"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Can't breathe",
            vital_signs={
                "heart_rate": 125,
                "respiratory_rate": 38,
                "systolic_bp": 110,
                "spo2": 82,  # Severe hypoxia
            },
            symptoms=["respiratory distress"],
        )

        assert result["triage_level"] == TriageLevel.LEVEL_1.value

    @pytest.mark.asyncio
    async def test_trauma_protocol_activation(self):
        """Test trauma protocol activation"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Motor vehicle accident",
            vital_signs={
                "heart_rate": 115,
                "respiratory_rate": 24,
                "systolic_bp": 105,
                "spo2": 94,
            },
            symptoms=["trauma", "chest pain", "confusion"],
        )

        assert result["emergency_type"] == EmergencyType.TRAUMA.value
        assert any("Trauma" in p["protocol"] for p in result["protocols_activated"])


@pytest.mark.unit
class TestResourceDetermination:
    """Test resource allocation based on triage"""

    @pytest.mark.asyncio
    async def test_level_1_gets_resuscitation_bay(self):
        """Test Level 1 patients go to resuscitation bay"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Cardiac arrest",
            vital_signs={
                "heart_rate": 0,
                "respiratory_rate": 0,
                "systolic_bp": 0,
                "spo2": 0,
            },
            symptoms=["unresponsive", "no_pulse"],
        )

        resources = result["action_plan"]["resource_mobilization"]
        assert resources["location"] == "Resuscitation Bay"
        assert "Physician" in resources["staff"]
        assert "Crash cart" in resources["equipment"]

    @pytest.mark.asyncio
    async def test_confidence_calculation(self):
        """Test confidence calculation with complete data"""
        agent = EmergencyResponseAgent()

        result = await agent.triage_patient(
            chief_complaint="Chest pain",
            vital_signs={
                "heart_rate": 95,
                "respiratory_rate": 18,
                "systolic_bp": 135,
                "spo2": 96,
            },
            symptoms=["chest pain", "diaphoresis"],
        )

        # Should have high confidence with complete data
        assert result["confidence"] >= 0.8
