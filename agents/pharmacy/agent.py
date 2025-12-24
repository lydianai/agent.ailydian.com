"""
Pharmacy Management Agent

Provides comprehensive pharmaceutical care:
- Prescription validation and verification
- Drug-drug interaction checking (DDI)
- Dosage calculation and optimization
- Medication reconciliation
- Adverse drug reaction (ADR) monitoring
- Inventory management support
- Medication therapy management (MTM)
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import math

from agents.base_agent import BaseAgent, AgentCapability
from core.logging import get_logger
from core.monitoring.metrics import track_agent_performance

logger = get_logger(__name__)


class PrescriptionStatus(str, Enum):
    """Prescription verification status"""
    APPROVED = "approved"
    PENDING_REVIEW = "pending_review"
    REQUIRES_CLARIFICATION = "requires_clarification"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class InteractionSeverity(str, Enum):
    """Drug-drug interaction severity"""
    CONTRAINDICATED = "contraindicated"  # Do not use together
    MAJOR = "major"  # Serious interaction
    MODERATE = "moderate"  # Monitor closely
    MINOR = "minor"  # Minimal clinical significance


class DosageError(str, Enum):
    """Types of dosage errors"""
    OVERDOSE = "overdose"  # Dose too high
    UNDERDOSE = "underdose"  # Dose too low
    FREQUENCY_ERROR = "frequency_error"  # Wrong frequency
    DURATION_ERROR = "duration_error"  # Wrong duration
    ROUTE_ERROR = "route_error"  # Wrong route


class MedicationRoute(str, Enum):
    """Medication administration routes"""
    ORAL = "oral"
    IV = "intravenous"
    IM = "intramuscular"
    SC = "subcutaneous"
    TOPICAL = "topical"
    INHALED = "inhaled"
    SUBLINGUAL = "sublingual"
    RECTAL = "rectal"


class PharmacyAgent(BaseAgent):
    """
    Pharmacy Management Agent

    Capabilities:
    - Prescription validation
    - Drug interaction checking
    - Dosage calculation
    - Medication reconciliation
    - ADR monitoring
    - Formulary compliance
    """

    def __init__(self):
        super().__init__(
            agent_id="pharmacy-agent",
            name="Pharmacy Management Agent",
            capabilities=[
                AgentCapability.PRESCRIPTION_VALIDATION,
                AgentCapability.DRUG_INTERACTION_CHECK,
                AgentCapability.DOSAGE_CALCULATION,
            ],
        )

        # Drug interaction database (expanded)
        self.drug_interactions = {
            ("Warfarin", "Aspirin"): {
                "severity": InteractionSeverity.MAJOR,
                "mechanism": "Increased bleeding risk (pharmacodynamic)",
                "management": "Monitor INR closely, consider PPI, bleeding precautions",
                "references": ["Lexicomp", "Micromedex"],
            },
            ("Warfarin", "Amiodarone"): {
                "severity": InteractionSeverity.MAJOR,
                "mechanism": "CYP2C9 inhibition - increased warfarin levels",
                "management": "Reduce warfarin dose by 30-50%, monitor INR q2-3 days",
                "references": ["Lexicomp"],
            },
            ("Clopidogrel", "Omeprazole"): {
                "severity": InteractionSeverity.MODERATE,
                "mechanism": "CYP2C19 inhibition - reduced clopidogrel activation",
                "management": "Use pantoprazole or H2 blocker instead",
                "references": ["FDA Warning"],
            },
            ("Simvastatin", "Clarithromycin"): {
                "severity": InteractionSeverity.MAJOR,
                "mechanism": "CYP3A4 inhibition - increased statin levels",
                "management": "Hold statin during macrolide therapy, risk of rhabdomyolysis",
                "references": ["Lexicomp"],
            },
            ("ACE inhibitors", "Potassium supplements"): {
                "severity": InteractionSeverity.MODERATE,
                "mechanism": "Additive hyperkalemia risk",
                "management": "Monitor potassium levels, avoid unless indicated",
                "references": ["Clinical guidelines"],
            },
            ("Digoxin", "Furosemide"): {
                "severity": InteractionSeverity.MODERATE,
                "mechanism": "Diuretic-induced hypokalemia increases digoxin toxicity",
                "management": "Monitor potassium and digoxin levels",
                "references": ["Lexicomp"],
            },
            ("Metformin", "Contrast dye"): {
                "severity": InteractionSeverity.MAJOR,
                "mechanism": "Lactic acidosis risk with impaired renal function",
                "management": "Hold metformin 48h before and after contrast with eGFR < 60",
                "references": ["FDA guidelines"],
            },
            ("SSRIs", "MAOIs"): {
                "severity": InteractionSeverity.CONTRAINDICATED,
                "mechanism": "Serotonin syndrome risk",
                "management": "Absolute contraindication - 2 week washout required",
                "references": ["FDA Warning"],
            },
        }

        # Dosing parameters database
        self.dosing_parameters = {
            "Vancomycin": {
                "loading_dose": "25-30 mg/kg IV",
                "maintenance_dose": "15-20 mg/kg IV q8-12h",
                "target_trough": "10-20 mcg/mL",
                "renal_adjustment": True,
                "monitoring": "Trough before 4th dose, renal function",
            },
            "Gentamicin": {
                "dose": "5-7 mg/kg IV q24h (extended interval)",
                "renal_adjustment": True,
                "monitoring": "Peak/trough, renal function, hearing",
                "max_duration": "7-14 days",
            },
            "Warfarin": {
                "initial_dose": "5 mg PO daily (2.5 mg if elderly or low weight)",
                "target_inr": "2.0-3.0 (most indications), 2.5-3.5 (mechanical valve)",
                "monitoring": "INR q2-3 days until stable, then monthly",
            },
            "Enoxaparin": {
                "treatment_dose": "1 mg/kg SC q12h or 1.5 mg/kg SC q24h",
                "prophylaxis_dose": "40 mg SC daily",
                "renal_adjustment": "Reduce dose if CrCl < 30",
                "monitoring": "Anti-Xa if needed, renal function, CBC",
            },
            "Insulin": {
                "types": ["Rapid-acting", "Short-acting", "Intermediate", "Long-acting"],
                "initial_dose": "0.5-1 unit/kg/day total daily dose",
                "monitoring": "Blood glucose q4-6h, HbA1c q3 months",
            },
        }

        # Medication safety limits
        self.safety_limits = {
            "Acetaminophen": {
                "max_single_dose": 1000,  # mg
                "max_daily_dose": 4000,  # mg
                "hepatotoxicity_threshold": 4000,
            },
            "Morphine": {
                "max_single_dose_oral": 30,  # mg for opioid-naive
                "max_single_dose_iv": 10,  # mg
                "monitoring": "Respiratory rate, sedation level",
            },
            "Potassium": {
                "max_infusion_rate": 10,  # mEq/hr peripheral
                "max_concentration_peripheral": 40,  # mEq/L
                "max_concentration_central": 100,  # mEq/L
            },
        }

        # Common adverse drug reactions
        self.adr_profiles = {
            "Statins": ["Myalgia", "Elevated liver enzymes", "Rhabdomyolysis (rare)"],
            "ACE inhibitors": ["Cough", "Angioedema", "Hyperkalemia", "Acute kidney injury"],
            "Beta-blockers": ["Bradycardia", "Hypotension", "Fatigue", "Bronchospasm"],
            "Antibiotics": ["Diarrhea", "Nausea", "Allergic reactions", "C. difficile infection"],
            "Opioids": ["Constipation", "Nausea", "Respiratory depression", "Sedation"],
        }

    async def perceive(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive pharmacy data

        Args:
            environment_data: {
                "prescription": {
                    "medication": str,
                    "dose": str,
                    "frequency": str,
                    "duration": str,
                    "route": str,
                    "indication": str,
                    "prescriber": str,
                },
                "patient": {
                    "patient_id": str,
                    "age": int,
                    "weight_kg": float,
                    "height_cm": float,
                    "allergies": list,
                    "current_medications": list,
                    "renal_function": dict,
                    "hepatic_function": dict,
                    "pregnancy_status": bool,
                },
                "clinical_data": {
                    "diagnosis": str,
                    "vital_signs": dict,
                    "lab_results": dict,
                },
            }

        Returns:
            Processed pharmacy perception
        """
        prescription = environment_data.get("prescription", {})
        patient = environment_data.get("patient", {})
        clinical_data = environment_data.get("clinical_data", {})

        # Extract prescription details
        medication = prescription.get("medication")
        dose = prescription.get("dose")
        frequency = prescription.get("frequency")
        route = prescription.get("route")

        # Extract patient factors
        patient_factors = {
            "age": patient.get("age"),
            "weight_kg": patient.get("weight_kg"),
            "bsa": self._calculate_bsa(patient.get("weight_kg"), patient.get("height_cm")),
            "allergies": patient.get("allergies", []),
            "current_medications": patient.get("current_medications", []),
            "renal_function": patient.get("renal_function", {}),
            "hepatic_function": patient.get("hepatic_function", {}),
            "pregnancy": patient.get("pregnancy_status", False),
        }

        return {
            "prescription": prescription,
            "patient_factors": patient_factors,
            "clinical_data": clinical_data,
            "timestamp": datetime.utcnow(),
        }

    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about prescription safety and appropriateness

        Returns:
            Pharmacy assessment with safety alerts
        """
        prescription = perception["prescription"]
        patient_factors = perception["patient_factors"]
        clinical_data = perception["clinical_data"]

        # Validate prescription completeness
        completeness_check = self._validate_prescription_completeness(prescription)

        # Check drug-drug interactions
        interaction_analysis = self._check_drug_interactions(
            prescription["medication"],
            patient_factors["current_medications"]
        )

        # Validate dosage
        dosage_validation = self._validate_dosage(
            prescription,
            patient_factors,
            clinical_data
        )

        # Check for allergies
        allergy_check = self._check_allergies(
            prescription["medication"],
            patient_factors["allergies"]
        )

        # Assess renal/hepatic adjustments needed
        adjustment_needed = self._assess_dose_adjustments(
            prescription,
            patient_factors
        )

        # Determine prescription status
        status = self._determine_prescription_status(
            completeness_check,
            interaction_analysis,
            dosage_validation,
            allergy_check
        )

        return {
            "status": status,
            "completeness_check": completeness_check,
            "interaction_analysis": interaction_analysis,
            "dosage_validation": dosage_validation,
            "allergy_check": allergy_check,
            "adjustment_needed": adjustment_needed,
        }

    async def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pharmacy recommendations and actions

        Returns:
            Pharmacy action plan
        """
        status = reasoning["status"]
        interaction_analysis = reasoning["interaction_analysis"]
        dosage_validation = reasoning["dosage_validation"]
        adjustment_needed = reasoning["adjustment_needed"]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            reasoning["interaction_analysis"],
            reasoning["dosage_validation"],
            reasoning["adjustment_needed"]
        )

        # Generate safety alerts
        safety_alerts = self._generate_safety_alerts(
            reasoning["interaction_analysis"],
            reasoning["allergy_check"],
            reasoning["dosage_validation"]
        )

        # Generate monitoring plan
        monitoring_plan = self._create_monitoring_plan(
            reasoning["interaction_analysis"],
            reasoning["dosage_validation"]
        )

        # Patient counseling points
        counseling_points = self._generate_counseling_points(
            interaction_analysis,
            dosage_validation
        )

        return {
            "verification_result": {
                "status": status,
                "approved": status == PrescriptionStatus.APPROVED.value,
            },
            "recommendations": recommendations,
            "safety_alerts": safety_alerts,
            "monitoring_plan": monitoring_plan,
            "counseling_points": counseling_points,
        }

    # ========================================================================
    # PRESCRIPTION VALIDATION
    # ========================================================================

    def _validate_prescription_completeness(self, prescription: dict) -> Dict:
        """Validate prescription has all required elements"""
        required_fields = ["medication", "dose", "frequency", "route", "duration"]
        missing_fields = []

        for field in required_fields:
            if not prescription.get(field):
                missing_fields.append(field)

        is_complete = len(missing_fields) == 0

        return {
            "is_complete": is_complete,
            "missing_fields": missing_fields,
        }

    def _check_drug_interactions(
        self, new_medication: str, current_medications: List[str]
    ) -> Dict:
        """Check for drug-drug interactions"""
        interactions_found = []

        for current_med in current_medications:
            # Check both directions
            interaction = self.drug_interactions.get((new_medication, current_med)) or \
                         self.drug_interactions.get((current_med, new_medication))

            if interaction:
                interactions_found.append({
                    "drug1": new_medication,
                    "drug2": current_med,
                    "severity": interaction["severity"].value,
                    "mechanism": interaction["mechanism"],
                    "management": interaction["management"],
                })

            # Check drug class interactions (simplified)
            class_interaction = self._check_drug_class_interaction(new_medication, current_med)
            if class_interaction:
                interactions_found.append(class_interaction)

        return {
            "has_interactions": len(interactions_found) > 0,
            "interactions": interactions_found,
            "highest_severity": self._get_highest_severity(interactions_found),
        }

    def _check_drug_class_interaction(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check for drug class interactions (simplified)"""
        # Example: ACE inhibitor + ARB
        ace_inhibitors = ["Lisinopril", "Enalapril", "Ramipril"]
        arbs = ["Losartan", "Valsartan", "Irbesartan"]

        if drug1 in ace_inhibitors and drug2 in arbs:
            return {
                "drug1": drug1,
                "drug2": drug2,
                "severity": InteractionSeverity.MODERATE.value,
                "mechanism": "Dual RAAS blockade - increased hyperkalemia risk",
                "management": "Generally not recommended together",
            }

        return None

    def _get_highest_severity(self, interactions: List[Dict]) -> Optional[str]:
        """Get highest severity level from interactions"""
        if not interactions:
            return None

        severity_order = [
            InteractionSeverity.CONTRAINDICATED.value,
            InteractionSeverity.MAJOR.value,
            InteractionSeverity.MODERATE.value,
            InteractionSeverity.MINOR.value,
        ]

        for severity in severity_order:
            if any(i["severity"] == severity for i in interactions):
                return severity

        return None

    def _validate_dosage(
        self, prescription: dict, patient_factors: dict, clinical_data: dict
    ) -> Dict:
        """Validate dosage appropriateness"""
        medication = prescription["medication"]
        dose_str = prescription.get("dose", "")

        errors = []
        warnings = []

        # Extract numeric dose (simplified)
        try:
            dose_value = float(''.join(filter(str.isdigit, dose_str.split()[0])))
        except:
            dose_value = 0

        # Check against safety limits
        if medication in self.safety_limits:
            limits = self.safety_limits[medication]

            if "max_single_dose" in limits and dose_value > limits["max_single_dose"]:
                errors.append({
                    "type": DosageError.OVERDOSE.value,
                    "message": f"Dose exceeds max single dose of {limits['max_single_dose']}",
                })

        # Age-specific checks
        age = patient_factors.get("age", 0)
        if age < 18:
            warnings.append("Pediatric dosing verification required")
        elif age > 65:
            warnings.append("Geriatric dosing - consider start low, go slow approach")

        # Weight-based dosing check
        weight = patient_factors.get("weight_kg")
        if weight and weight < 50:
            warnings.append("Low body weight - consider dose adjustment")

        is_appropriate = len(errors) == 0

        return {
            "is_appropriate": is_appropriate,
            "errors": errors,
            "warnings": warnings,
        }

    def _check_allergies(self, medication: str, allergies: List[str]) -> Dict:
        """Check for allergy contraindications"""
        allergy_found = False
        cross_reactivity_risk = False

        for allergy in allergies:
            # Direct match
            if medication.lower() in allergy.lower() or allergy.lower() in medication.lower():
                allergy_found = True
                break

            # Cross-reactivity (simplified)
            if "penicillin" in allergy.lower() and "cephalosporin" in medication.lower():
                cross_reactivity_risk = True

        return {
            "allergy_found": allergy_found,
            "cross_reactivity_risk": cross_reactivity_risk,
            "safe_to_administer": not allergy_found,
        }

    def _assess_dose_adjustments(self, prescription: dict, patient_factors: dict) -> Dict:
        """Assess if dose adjustments needed for renal/hepatic impairment"""
        medication = prescription["medication"]
        adjustments_needed = []

        # Renal adjustment
        renal_function = patient_factors.get("renal_function", {})
        egfr = renal_function.get("egfr")

        if medication in self.dosing_parameters:
            params = self.dosing_parameters[medication]

            if params.get("renal_adjustment") and egfr and egfr < 60:
                adjustments_needed.append({
                    "type": "renal",
                    "severity": "moderate" if egfr >= 30 else "severe",
                    "recommendation": f"Reduce dose or extend interval for CrCl {egfr}",
                })

        # Hepatic adjustment (simplified)
        hepatic_function = patient_factors.get("hepatic_function", {})
        alt = hepatic_function.get("alt", 0)

        if alt > 3 * 40:  # > 3x ULN
            adjustments_needed.append({
                "type": "hepatic",
                "severity": "severe",
                "recommendation": "Consider dose reduction for hepatic impairment",
            })

        return {
            "adjustments_needed": len(adjustments_needed) > 0,
            "adjustments": adjustments_needed,
        }

    def _determine_prescription_status(
        self, completeness: dict, interactions: dict, dosage: dict, allergy: dict
    ) -> str:
        """Determine overall prescription status"""
        # Reject if allergy found
        if allergy["allergy_found"]:
            return PrescriptionStatus.REJECTED.value

        # Reject if contraindicated interaction
        if interactions["highest_severity"] == InteractionSeverity.CONTRAINDICATED.value:
            return PrescriptionStatus.REJECTED.value

        # Pending if incomplete
        if not completeness["is_complete"]:
            return PrescriptionStatus.REQUIRES_CLARIFICATION.value

        # Pending if dosage errors
        if not dosage["is_appropriate"]:
            return PrescriptionStatus.REQUIRES_CLARIFICATION.value

        # On hold if major interaction
        if interactions["highest_severity"] == InteractionSeverity.MAJOR.value:
            return PrescriptionStatus.ON_HOLD.value

        # Otherwise approved
        return PrescriptionStatus.APPROVED.value

    # ========================================================================
    # CALCULATIONS
    # ========================================================================

    def _calculate_bsa(self, weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[float]:
        """Calculate body surface area using Mosteller formula"""
        if not weight_kg or not height_cm:
            return None

        bsa = math.sqrt((weight_kg * height_cm) / 3600)
        return round(bsa, 2)

    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================

    def _generate_recommendations(
        self, interactions: dict, dosage: dict, adjustments: dict
    ) -> List[str]:
        """Generate pharmacy recommendations"""
        recommendations = []

        # Interaction recommendations
        for interaction in interactions.get("interactions", []):
            recommendations.append(f"DDI Alert: {interaction['management']}")

        # Dosage recommendations
        for error in dosage.get("errors", []):
            recommendations.append(f"Dosage: {error['message']}")

        # Adjustment recommendations
        for adjustment in adjustments.get("adjustments", []):
            recommendations.append(f"{adjustment['type'].capitalize()}: {adjustment['recommendation']}")

        return recommendations

    def _generate_safety_alerts(
        self, interactions: dict, allergy: dict, dosage: dict
    ) -> List[Dict]:
        """Generate critical safety alerts"""
        alerts = []

        # Allergy alert
        if allergy["allergy_found"]:
            alerts.append({
                "severity": "critical",
                "type": "allergy",
                "message": "ALLERGY CONTRAINDICATION - DO NOT DISPENSE",
            })

        # Contraindicated interaction
        if interactions["highest_severity"] == InteractionSeverity.CONTRAINDICATED.value:
            alerts.append({
                "severity": "critical",
                "type": "interaction",
                "message": "CONTRAINDICATED DRUG INTERACTION",
            })

        # Major interaction
        if interactions["highest_severity"] == InteractionSeverity.MAJOR.value:
            alerts.append({
                "severity": "major",
                "type": "interaction",
                "message": "MAJOR DRUG INTERACTION - Pharmacist review required",
            })

        # Dosage errors
        for error in dosage.get("errors", []):
            alerts.append({
                "severity": "major",
                "type": "dosage",
                "message": error["message"],
            })

        return alerts

    def _create_monitoring_plan(self, interactions: dict, dosage: dict) -> List[str]:
        """Create medication monitoring plan"""
        monitoring = []

        # Interaction-specific monitoring
        for interaction in interactions.get("interactions", []):
            if "Monitor" in interaction["management"]:
                monitoring.append(interaction["management"])

        # Medication-specific monitoring (from dosing parameters)
        # This would be expanded in production

        return monitoring

    def _generate_counseling_points(self, interactions: dict, dosage: dict) -> List[str]:
        """Generate patient counseling points"""
        points = [
            "Take medication as prescribed",
            "Do not stop medication without consulting prescriber",
            "Report any side effects to healthcare provider",
        ]

        # Interaction-specific counseling
        if interactions["has_interactions"]:
            points.append("Important drug interactions noted - follow monitoring plan")

        return points

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    @track_agent_performance("Pharmacy Agent")
    async def verify_prescription(
        self,
        prescription: dict,
        patient_data: dict,
        clinical_data: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive prescription verification

        Args:
            prescription: Prescription details
            patient_data: Patient demographics and medical history
            clinical_data: Clinical context (optional)

        Returns:
            Verification result with recommendations and alerts
        """
        # Build environment data
        environment_data = {
            "prescription": prescription,
            "patient": patient_data,
            "clinical_data": clinical_data or {},
        }

        # Execute agent cycle
        perception = await self.perceive(environment_data)
        reasoning = await self.reason(perception)
        action_plan = await self.act(reasoning)

        # Combine results
        return {
            "prescription": prescription,
            "patient_id": patient_data.get("patient_id"),
            "verification_result": action_plan["verification_result"],
            "recommendations": action_plan["recommendations"],
            "safety_alerts": action_plan["safety_alerts"],
            "monitoring_plan": action_plan["monitoring_plan"],
            "counseling_points": action_plan["counseling_points"],
            "timestamp": perception["timestamp"].isoformat(),
        }
