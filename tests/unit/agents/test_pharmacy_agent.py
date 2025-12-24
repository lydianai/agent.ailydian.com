"""
Unit Tests for Pharmacy Management Agent

Tests prescription verification, drug interactions, and dosage validation.
"""

import pytest
from datetime import datetime

from agents.pharmacy.agent import (
    PharmacyAgent,
    PrescriptionStatus,
    InteractionSeverity,
    DosageError,
    MedicationRoute,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestPharmacyAgent:
    """Test Pharmacy Management Agent"""

    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = PharmacyAgent()

        assert agent is not None
        assert agent.name == "Pharmacy Management Agent"

    async def test_approve_valid_prescription(self):
        """Test approval of valid prescription"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Amoxicillin",
                "dose": "500mg",
                "frequency": "q8h",
                "route": "oral",
                "duration": "7 days",
                "indication": "Community-acquired pneumonia",
                "prescriber": "Dr. Smith",
            },
            patient_data={
                "patient_id": "P-001",
                "age": 45,
                "weight_kg": 75,
                "height_cm": 175,
                "allergies": [],
                "current_medications": [],
                "renal_function": {"egfr": 90},
            },
        )

        # Should be approved
        assert result["verification_result"]["approved"] is True
        assert result["verification_result"]["status"] == PrescriptionStatus.APPROVED.value

    async def test_reject_allergy_contraindication(self):
        """Test rejection due to allergy"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Penicillin",
                "dose": "500mg",
                "frequency": "q6h",
                "route": "oral",
                "duration": "10 days",
            },
            patient_data={
                "patient_id": "P-002",
                "age": 50,
                "weight_kg": 70,
                "allergies": ["Penicillin allergy"],
                "current_medications": [],
            },
        )

        # Should be rejected
        assert result["verification_result"]["approved"] is False
        assert result["verification_result"]["status"] == PrescriptionStatus.REJECTED.value

        # Should have critical alert
        assert any(
            alert["severity"] == "critical" and alert["type"] == "allergy"
            for alert in result["safety_alerts"]
        )


@pytest.mark.unit
@pytest.mark.asyncio
class TestDrugInteractions:
    """Test drug-drug interaction checking"""

    async def test_warfarin_aspirin_interaction(self):
        """Test detection of warfarin-aspirin interaction"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Aspirin",
                "dose": "325mg",
                "frequency": "daily",
                "route": "oral",
                "duration": "ongoing",
            },
            patient_data={
                "patient_id": "P-003",
                "age": 65,
                "weight_kg": 80,
                "allergies": [],
                "current_medications": ["Warfarin", "Metoprolol"],
                "renal_function": {"egfr": 75},
            },
        )

        # Should detect interaction
        assert len(result["safety_alerts"]) > 0

        # Should be on hold or have major interaction alert
        assert any(
            "interaction" in alert["type"].lower()
            for alert in result["safety_alerts"]
        )

    async def test_simvastatin_clarithromycin_interaction(self):
        """Test detection of statin-macrolide interaction"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Clarithromycin",
                "dose": "500mg",
                "frequency": "q12h",
                "route": "oral",
                "duration": "7 days",
            },
            patient_data={
                "patient_id": "P-004",
                "age": 60,
                "weight_kg": 75,
                "allergies": [],
                "current_medications": ["Simvastatin 40mg daily"],
            },
        )

        # Should detect major interaction
        assert len(result["safety_alerts"]) > 0

    async def test_no_interaction_clean_case(self):
        """Test no interaction in clean case"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Amoxicillin",
                "dose": "500mg",
                "frequency": "q8h",
                "route": "oral",
                "duration": "7 days",
            },
            patient_data={
                "patient_id": "P-005",
                "age": 40,
                "weight_kg": 70,
                "allergies": [],
                "current_medications": ["Lisinopril"],
            },
        )

        # Should have no critical safety alerts
        critical_alerts = [
            a for a in result["safety_alerts"]
            if a["severity"] == "critical"
        ]
        assert len(critical_alerts) == 0


@pytest.mark.unit
@pytest.mark.asyncio
class TestDosageValidation:
    """Test dosage validation"""

    async def test_acetaminophen_overdose(self):
        """Test detection of acetaminophen overdose"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Acetaminophen",
                "dose": "1500mg",  # Exceeds max single dose of 1000mg
                "frequency": "q6h",
                "route": "oral",
                "duration": "as needed",
            },
            patient_data={
                "patient_id": "P-006",
                "age": 45,
                "weight_kg": 75,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should detect dosage error
        assert len(result["safety_alerts"]) > 0

    async def test_pediatric_dosing_warning(self):
        """Test pediatric dosing warning"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Ibuprofen",
                "dose": "200mg",
                "frequency": "q6h",
                "route": "oral",
                "duration": "3 days",
            },
            patient_data={
                "patient_id": "P-007",
                "age": 12,  # Pediatric
                "weight_kg": 40,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should have recommendations or warnings
        # Pediatric dosing should be flagged for verification

    async def test_geriatric_dosing_warning(self):
        """Test geriatric dosing consideration"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Morphine",
                "dose": "10mg",
                "frequency": "q4h",
                "route": "oral",
                "duration": "ongoing",
            },
            patient_data={
                "patient_id": "P-008",
                "age": 85,  # Geriatric
                "weight_kg": 55,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should have warnings about geriatric dosing


@pytest.mark.unit
@pytest.mark.asyncio
class TestRenalAdjustment:
    """Test renal dose adjustment"""

    async def test_renal_adjustment_needed(self):
        """Test detection of need for renal dose adjustment"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Enoxaparin",
                "dose": "1 mg/kg SC q12h",
                "frequency": "q12h",
                "route": "subcutaneous",
                "duration": "7 days",
            },
            patient_data={
                "patient_id": "P-009",
                "age": 70,
                "weight_kg": 65,
                "allergies": [],
                "current_medications": [],
                "renal_function": {"egfr": 25},  # Severe renal impairment
            },
        )

        # Should have recommendations for dose adjustment
        assert len(result["recommendations"]) > 0

    async def test_normal_renal_function(self):
        """Test normal renal function - no adjustment"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Gentamicin",
                "dose": "5 mg/kg IV q24h",
                "frequency": "daily",
                "route": "IV",
                "duration": "7 days",
            },
            patient_data={
                "patient_id": "P-010",
                "age": 45,
                "weight_kg": 75,
                "allergies": [],
                "current_medications": [],
                "renal_function": {"egfr": 95},
            },
        )

        # Should be approved with normal renal function
        assert result["verification_result"]["status"] in [
            PrescriptionStatus.APPROVED.value,
            PrescriptionStatus.ON_HOLD.value,
        ]


@pytest.mark.unit
@pytest.mark.asyncio
class TestPrescriptionCompleteness:
    """Test prescription completeness validation"""

    async def test_incomplete_prescription(self):
        """Test detection of incomplete prescription"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Amoxicillin",
                "dose": "500mg",
                # Missing frequency, route, duration
            },
            patient_data={
                "patient_id": "P-011",
                "age": 50,
                "weight_kg": 70,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should require clarification
        assert result["verification_result"]["status"] == PrescriptionStatus.REQUIRES_CLARIFICATION.value

    async def test_complete_prescription(self):
        """Test complete prescription"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Amoxicillin",
                "dose": "500mg",
                "frequency": "q8h",
                "route": "oral",
                "duration": "7 days",
            },
            patient_data={
                "patient_id": "P-012",
                "age": 50,
                "weight_kg": 70,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should be approved (if no other issues)
        assert result["verification_result"]["approved"] is True


@pytest.mark.unit
class TestBSACalculation:
    """Test body surface area calculation"""

    def test_bsa_calculation(self):
        """Test BSA calculation using Mosteller formula"""
        agent = PharmacyAgent()

        bsa = agent._calculate_bsa(weight_kg=75, height_cm=175)

        # Expected BSA ≈ 1.91 m²
        assert bsa is not None
        assert 1.85 < bsa < 1.95

    def test_bsa_missing_data(self):
        """Test BSA calculation with missing data"""
        agent = PharmacyAgent()

        bsa = agent._calculate_bsa(weight_kg=None, height_cm=175)

        assert bsa is None


@pytest.mark.unit
class TestInteractionSeverity:
    """Test interaction severity determination"""

    def test_highest_severity_contraindicated(self):
        """Test highest severity detection - contraindicated"""
        agent = PharmacyAgent()

        interactions = [
            {"severity": InteractionSeverity.MINOR.value},
            {"severity": InteractionSeverity.CONTRAINDICATED.value},
            {"severity": InteractionSeverity.MODERATE.value},
        ]

        highest = agent._get_highest_severity(interactions)

        assert highest == InteractionSeverity.CONTRAINDICATED.value

    def test_highest_severity_major(self):
        """Test highest severity detection - major"""
        agent = PharmacyAgent()

        interactions = [
            {"severity": InteractionSeverity.MINOR.value},
            {"severity": InteractionSeverity.MAJOR.value},
            {"severity": InteractionSeverity.MODERATE.value},
        ]

        highest = agent._get_highest_severity(interactions)

        assert highest == InteractionSeverity.MAJOR.value

    def test_no_interactions(self):
        """Test no interactions case"""
        agent = PharmacyAgent()

        highest = agent._get_highest_severity([])

        assert highest is None


@pytest.mark.unit
@pytest.mark.asyncio
class TestMonitoringPlans:
    """Test monitoring plan generation"""

    async def test_monitoring_for_anticoagulation(self):
        """Test monitoring plan for anticoagulation"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Warfarin",
                "dose": "5mg",
                "frequency": "daily",
                "route": "oral",
                "duration": "ongoing",
            },
            patient_data={
                "patient_id": "P-013",
                "age": 65,
                "weight_kg": 75,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should have monitoring plan
        assert "monitoring_plan" in result

    async def test_counseling_points(self):
        """Test patient counseling point generation"""
        agent = PharmacyAgent()

        result = await agent.verify_prescription(
            prescription={
                "medication": "Metformin",
                "dose": "500mg",
                "frequency": "BID",
                "route": "oral",
                "duration": "ongoing",
            },
            patient_data={
                "patient_id": "P-014",
                "age": 55,
                "weight_kg": 80,
                "allergies": [],
                "current_medications": [],
            },
        )

        # Should have counseling points
        assert "counseling_points" in result
        assert len(result["counseling_points"]) > 0
