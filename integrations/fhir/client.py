"""
HL7 FHIR Client

Real integration with FHIR servers (Epic, Cerner, etc.)
Handles patient data exchange using FHIR R4 standard.
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.encounter import Encounter

from core.config import settings
from core.logging import get_logger

logger = get_logger()


class FHIRClient:
    """
    FHIR R4 client for EHR integration

    Supports:
    - Epic FHIR API
    - Cerner FHIR API
    - Generic FHIR R4 servers
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.hl7_fhir_base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json"
            }
        )

        logger.info(f"FHIR client initialized: {self.base_url}")

    # ========================================================================
    # PATIENT OPERATIONS
    # ========================================================================

    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get patient resource by ID

        Args:
            patient_id: FHIR patient ID

        Returns:
            Patient resource as dict
        """

        try:
            response = await self.client.get(f"/Patient/{patient_id}")
            response.raise_for_status()

            patient_data = response.json()

            # Parse using fhir.resources
            patient = Patient.parse_obj(patient_data)

            return self._patient_to_dict(patient)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Patient not found: {patient_id}")
                return None
            logger.error(f"FHIR API error: {e}")
            raise

        except Exception as e:
            logger.error(f"Error fetching patient: {e}")
            raise

    async def search_patients(
        self,
        family_name: Optional[str] = None,
        given_name: Optional[str] = None,
        birthdate: Optional[str] = None,
        identifier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for patients

        Args:
            family_name: Last name
            given_name: First name
            birthdate: Date of birth (YYYY-MM-DD)
            identifier: MRN or other identifier

        Returns:
            List of matching patients
        """

        params = {}
        if family_name:
            params["family"] = family_name
        if given_name:
            params["given"] = given_name
        if birthdate:
            params["birthdate"] = birthdate
        if identifier:
            params["identifier"] = identifier

        try:
            response = await self.client.get("/Patient", params=params)
            response.raise_for_status()

            bundle = response.json()

            patients = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                patient = Patient.parse_obj(resource)
                patients.append(self._patient_to_dict(patient))

            return patients

        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            raise

    # ========================================================================
    # OBSERVATION OPERATIONS (Vitals, Labs)
    # ========================================================================

    async def get_observations(
        self,
        patient_id: str,
        category: Optional[str] = None,
        code: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patient observations (vital signs, labs)

        Args:
            patient_id: FHIR patient ID
            category: vital-signs, laboratory, etc.
            code: LOINC code for specific observation
            date: Date filter (ge2024-01-01)

        Returns:
            List of observations
        """

        params = {
            "patient": patient_id,
            "_sort": "-date"
        }

        if category:
            params["category"] = category

        if code:
            params["code"] = code

        if date:
            params["date"] = date

        try:
            response = await self.client.get("/Observation", params=params)
            response.raise_for_status()

            bundle = response.json()

            observations = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                obs = Observation.parse_obj(resource)
                observations.append(self._observation_to_dict(obs))

            return observations

        except Exception as e:
            logger.error(f"Error fetching observations: {e}")
            raise

    async def create_observation(
        self,
        patient_id: str,
        code: str,
        value: float,
        unit: str,
        category: str = "vital-signs"
    ) -> Dict[str, Any]:
        """
        Create new observation (e.g., vital signs from our monitoring)

        Args:
            patient_id: FHIR patient ID
            code: LOINC code
            value: Numeric value
            unit: Unit of measure
            category: Observation category

        Returns:
            Created observation
        """

        observation = {
            "resourceType": "Observation",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": category
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": code
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.utcnow().isoformat(),
            "valueQuantity": {
                "value": value,
                "unit": unit
            }
        }

        try:
            response = await self.client.post("/Observation", json=observation)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error creating observation: {e}")
            raise

    # ========================================================================
    # CONDITION OPERATIONS (Diagnoses)
    # ========================================================================

    async def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get patient conditions (diagnoses, problems)

        Args:
            patient_id: FHIR patient ID

        Returns:
            List of conditions
        """

        try:
            response = await self.client.get(
                "/Condition",
                params={"patient": patient_id, "_sort": "-recorded-date"}
            )
            response.raise_for_status()

            bundle = response.json()

            conditions = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                condition = Condition.parse_obj(resource)
                conditions.append(self._condition_to_dict(condition))

            return conditions

        except Exception as e:
            logger.error(f"Error fetching conditions: {e}")
            raise

    # ========================================================================
    # MEDICATION OPERATIONS
    # ========================================================================

    async def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get patient medication requests

        Args:
            patient_id: FHIR patient ID

        Returns:
            List of medications
        """

        try:
            response = await self.client.get(
                "/MedicationRequest",
                params={"patient": patient_id, "status": "active"}
            )
            response.raise_for_status()

            bundle = response.json()

            medications = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                med = MedicationRequest.parse_obj(resource)
                medications.append(self._medication_to_dict(med))

            return medications

        except Exception as e:
            logger.error(f"Error fetching medications: {e}")
            raise

    # ========================================================================
    # ENCOUNTER OPERATIONS
    # ========================================================================

    async def get_encounters(
        self,
        patient_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patient encounters

        Args:
            patient_id: FHIR patient ID
            status: in-progress, finished, etc.

        Returns:
            List of encounters
        """

        params = {"patient": patient_id}
        if status:
            params["status"] = status

        try:
            response = await self.client.get("/Encounter", params=params)
            response.raise_for_status()

            bundle = response.json()

            encounters = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                encounter = Encounter.parse_obj(resource)
                encounters.append(self._encounter_to_dict(encounter))

            return encounters

        except Exception as e:
            logger.error(f"Error fetching encounters: {e}")
            raise

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _patient_to_dict(self, patient: Patient) -> Dict[str, Any]:
        """Convert FHIR Patient to simplified dict"""

        name = patient.name[0] if patient.name else None

        return {
            "patient_id": patient.id,
            "family_name": name.family if name else None,
            "given_name": name.given[0] if name and name.given else None,
            "birthdate": str(patient.birthDate) if patient.birthDate else None,
            "gender": patient.gender,
            "identifiers": [
                {"system": id.system, "value": id.value}
                for id in (patient.identifier or [])
            ]
        }

    def _observation_to_dict(self, obs: Observation) -> Dict[str, Any]:
        """Convert FHIR Observation to simplified dict"""

        code = obs.code.coding[0] if obs.code and obs.code.coding else None

        value = None
        unit = None
        if obs.valueQuantity:
            value = obs.valueQuantity.value
            unit = obs.valueQuantity.unit

        return {
            "observation_id": obs.id,
            "code": code.code if code else None,
            "display": code.display if code else None,
            "value": value,
            "unit": unit,
            "effective_datetime": str(obs.effectiveDateTime) if obs.effectiveDateTime else None,
            "status": obs.status
        }

    def _condition_to_dict(self, condition: Condition) -> Dict[str, Any]:
        """Convert FHIR Condition to simplified dict"""

        code = condition.code.coding[0] if condition.code and condition.code.coding else None

        return {
            "condition_id": condition.id,
            "code": code.code if code else None,
            "display": code.display if code else None,
            "clinical_status": condition.clinicalStatus.coding[0].code if condition.clinicalStatus else None,
            "recorded_date": str(condition.recordedDate) if condition.recordedDate else None
        }

    def _medication_to_dict(self, med: MedicationRequest) -> Dict[str, Any]:
        """Convert FHIR MedicationRequest to simplified dict"""

        medication = med.medicationCodeableConcept
        code = medication.coding[0] if medication and medication.coding else None

        return {
            "medication_id": med.id,
            "medication_code": code.code if code else None,
            "medication_name": code.display if code else None,
            "status": med.status,
            "intent": med.intent,
            "authored_on": str(med.authoredOn) if med.authoredOn else None
        }

    def _encounter_to_dict(self, encounter: Encounter) -> Dict[str, Any]:
        """Convert FHIR Encounter to simplified dict"""

        return {
            "encounter_id": encounter.id,
            "status": encounter.status,
            "class_code": encounter.class_fhir.code if encounter.class_fhir else None,
            "period_start": str(encounter.period.start) if encounter.period and encounter.period.start else None,
            "period_end": str(encounter.period.end) if encounter.period and encounter.period.end else None
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# ============================================================================
# FACTORY
# ============================================================================

def create_fhir_client(base_url: Optional[str] = None) -> FHIRClient:
    """Create FHIR client"""
    return FHIRClient(base_url)
