"""
Tests for Clinical Decision Agent

Run with: pytest tests/test_clinical_decision.py -v
"""

import pytest
from uuid import uuid4

from agents.clinical_decision.agent import ClinicalDecisionAgent
from core.agents.base_agent import Observation


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def agent():
    """Create clinical decision agent for testing"""
    return ClinicalDecisionAgent(agent_id="test-agent-001")


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "patient_id": str(uuid4()),
        "encounter_id": str(uuid4()),
        "chief_complaint": "chest pain and shortness of breath",
        "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
        "vitals": {
            "heart_rate": 105,
            "blood_pressure_systolic": 145,
            "blood_pressure_diastolic": 92,
            "temperature": 37.2,
            "oxygen_saturation": 94.0,
            "respiratory_rate": 22
        },
        "medical_history": ["hypertension", "type 2 diabetes", "hyperlipidemia"],
        "current_medications": ["metformin 1000mg BID", "lisinopril 10mg daily", "atorvastatin 40mg daily"],
        "labs": {
            "troponin": 0.8,
            "BNP": 450,
            "creatinine": 1.1,
            "glucose": 145
        }
    }


# ============================================================================
# TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_perceive(agent, sample_patient_data):
    """Test perception of clinical data"""
    observation = await agent.perceive(sample_patient_data)

    assert isinstance(observation, Observation)
    assert observation.patient_id == sample_patient_data["patient_id"]
    assert observation.data == sample_patient_data


@pytest.mark.asyncio
async def test_perceive_missing_required_field(agent):
    """Test perception with missing required field"""
    with pytest.raises(ValueError, match="Missing required field"):
        await agent.perceive({"symptoms": ["fever"]})


@pytest.mark.asyncio
async def test_build_clinical_prompt(agent, sample_patient_data):
    """Test clinical prompt building"""
    prompt = agent._build_clinical_prompt(sample_patient_data)

    assert "chest pain" in prompt.lower()
    assert "troponin" in prompt.lower()
    assert "differential diagnosis" in prompt.lower()
    assert "json" in prompt.lower()


@pytest.mark.asyncio
async def test_drug_interaction_check(agent):
    """Test drug interaction detection"""
    warnings = agent._check_drug_interactions(
        current_meds=["warfarin"],
        new_meds=["aspirin 81mg daily"]
    )

    assert len(warnings) > 0
    assert any("warfarin" in w["interaction"].lower() for w in warnings)


@pytest.mark.asyncio
async def test_urgent_findings_detection(agent):
    """Test urgent findings flagging"""
    parameters = {
        "differential_diagnosis": [
            {
                "diagnosis": "STEMI",
                "probability": 0.85,
                "severity": "critical"
            }
        ],
        "recommended_tests": [
            {
                "test": "ECG",
                "urgency": "immediate",
                "reason": "Rule out ACS"
            }
        ]
    }

    urgent_flags = agent._check_urgent_findings(parameters)

    assert len(urgent_flags) > 0
    assert any("CRITICAL" in flag for flag in urgent_flags)
    assert any("IMMEDIATE" in flag for flag in urgent_flags)


def test_agent_initialization(agent):
    """Test agent initialization"""
    assert agent.agent_type == "clinical_decision"
    assert agent.agent_version == "1.0.0"
    assert agent.medical_knowledge is not None


def test_metrics_initialization(agent):
    """Test metrics are initialized correctly"""
    metrics = agent.get_metrics()

    assert metrics["total_decisions"] == 0
    assert metrics["successful_decisions"] == 0
    assert metrics["failed_decisions"] == 0


# ============================================================================
# INTEGRATION TEST (requires LLM API key)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skipif(
    condition=True,  # Skip by default (requires API key)
    reason="Requires OpenAI/Anthropic API key"
)
async def test_full_clinical_reasoning(agent, sample_patient_data):
    """
    Full integration test: perceive → reason → act

    NOTE: This test requires valid LLM API keys and will make actual API calls.
    Enable by setting skipif condition to False and providing API keys.
    """
    # Perceive
    observation = await agent.perceive(sample_patient_data)

    # Reason
    decision = await agent.reason(observation)

    assert decision.confidence >= 0.0
    assert decision.confidence <= 1.0
    assert len(decision.parameters["differential_diagnosis"]) > 0

    # Act
    result = await agent.act(decision)

    assert result.success is True
    assert "clinical_output" in result.details


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
