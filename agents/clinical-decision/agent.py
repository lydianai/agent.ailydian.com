"""
Clinical Decision Agent

AI-powered clinical decision support using LLMs (GPT-4, Claude).

Capabilities:
- Differential diagnosis generation
- Treatment plan recommendations
- Drug interaction analysis
- Evidence-based medicine guidance
"""

from typing import Any, Dict, List, Optional
import json
import asyncio

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from core.agents.base_agent import (
    BaseHealthcareAgent, Observation, Decision, ActionResult
)
from core.config import settings
from core.logging import get_logger
from core.database import DecisionOutcome

logger = get_logger()


# ============================================================================
# CLINICAL DECISION AGENT
# ============================================================================

class ClinicalDecisionAgent(BaseHealthcareAgent):
    """
    Clinical decision support agent

    Uses GPT-4/Claude to analyze patient data and provide:
    1. Differential diagnoses with probabilities
    2. Recommended diagnostic tests
    3. Treatment suggestions
    4. Drug interaction warnings
    """

    def __init__(self, agent_id: str = "clinical-decision-001"):
        super().__init__(
            agent_id=agent_id,
            agent_type="clinical_decision",
            agent_version="1.0.0"
        )

        # Initialize LLM clients
        if settings.has_openai:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            self.openai_client = None
            logger.warning("OpenAI not configured")

        if settings.has_anthropic:
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            logger.info("Anthropic client initialized")
        else:
            self.anthropic_client = None
            logger.warning("Anthropic not configured")

        # Medical knowledge base (simplified - in production would use UMLS, SNOMED CT)
        self.medical_knowledge = self._load_medical_knowledge()

    def _load_medical_knowledge(self) -> Dict[str, Any]:
        """
        Load medical knowledge base

        In production, this would connect to:
        - UMLS (Unified Medical Language System)
        - SNOMED CT (clinical terminology)
        - RxNorm (medications)
        - Clinical practice guidelines
        """
        return {
            "guidelines": {
                "chest_pain": {
                    "reference": "AHA/ACC 2024 Chest Pain Guidelines",
                    "critical_findings": ["elevated troponin", "ECG changes", "hemodynamic instability"],
                    "immediate_actions": ["ECG within 10 minutes", "troponin", "cardiology consult"]
                },
                "sepsis": {
                    "reference": "Surviving Sepsis Campaign 2023",
                    "sirs_criteria": ["temp >38 or <36", "HR >90", "RR >20", "WBC >12k or <4k"],
                    "immediate_actions": ["blood cultures", "broad-spectrum antibiotics", "lactate"]
                }
            },
            "drug_interactions": {
                "warfarin": ["aspirin", "NSAIDs", "clopidogrel"],
                "metformin": ["contrast dye (hold 48h)", "alcohol"],
                "statins": ["gemfibrozil", "cyclosporine"]
            }
        }

    # ========================================================================
    # CORE METHODS
    # ========================================================================

    async def perceive(self, data: Dict[str, Any]) -> Observation:
        """
        Process clinical input data

        Expected input format:
        {
            "patient_id": "uuid",
            "encounter_id": "uuid",
            "chief_complaint": "chest pain",
            "vitals": {"HR": 105, "BP": "145/92", ...},
            "symptoms": ["chest pain", "shortness of breath"],
            "medical_history": ["hypertension", "diabetes"],
            "current_medications": ["metformin", "lisinopril"],
            "labs": {"troponin": 0.8, "BNP": 450, ...}
        }
        """
        logger.debug("Perceiving clinical data", data_keys=list(data.keys()))

        # Validate required fields
        required_fields = ["patient_id", "chief_complaint"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Structure observation
        observation = Observation(
            data=data,
            source="clinical_decision_agent",
            patient_id=data.get("patient_id"),
            encounter_id=data.get("encounter_id")
        )

        return observation

    async def reason(self, observation: Observation) -> Decision:
        """
        Clinical reasoning using LLMs

        Process:
        1. Extract patient data
        2. Build clinical context
        3. Query LLM for differential diagnosis
        4. Parse and validate response
        5. Check drug interactions
        6. Generate recommendations
        """
        data = observation.data

        # Build clinical prompt
        prompt = self._build_clinical_prompt(data)

        # Get diagnosis from LLM (try GPT-4 first, fallback to Claude)
        llm_response = await self._query_llm(prompt)

        # Parse LLM response
        diagnosis_data = self._parse_llm_response(llm_response)

        # Check for drug interactions
        drug_warnings = self._check_drug_interactions(
            data.get("current_medications", []),
            diagnosis_data.get("recommended_medications", [])
        )

        # Build decision
        decision = Decision(
            action="clinical_diagnosis",
            parameters={
                "differential_diagnosis": diagnosis_data["differential_diagnosis"],
                "recommended_tests": diagnosis_data["recommended_tests"],
                "treatment_suggestions": diagnosis_data["treatment_suggestions"],
                "drug_warnings": drug_warnings
            },
            confidence=diagnosis_data["confidence"],
            reasoning=diagnosis_data["reasoning_steps"],
            knowledge_sources=diagnosis_data["knowledge_sources"],
            explanation=diagnosis_data["explanation"]
        )

        return decision

    async def act(self, decision: Decision) -> ActionResult:
        """
        Execute clinical decision

        Actions:
        1. Format output for clinician
        2. Create alerts if urgent findings
        3. Return structured recommendations
        """
        try:
            # Format output
            output = {
                "primary_diagnosis": decision.parameters["differential_diagnosis"][0]
                if decision.parameters["differential_diagnosis"] else None,
                "differential_diagnoses": decision.parameters["differential_diagnosis"],
                "confidence": decision.confidence,
                "recommended_tests": decision.parameters["recommended_tests"],
                "treatment_suggestions": decision.parameters["treatment_suggestions"],
                "drug_warnings": decision.parameters["drug_warnings"],
                "requires_human_review": decision.requires_human_review,
                "explanation": decision.explanation
            }

            # Check for urgent findings
            urgent_flags = self._check_urgent_findings(decision.parameters)

            result = ActionResult(
                success=True,
                outcome=DecisionOutcome.SUCCESS,
                details={
                    "clinical_output": output,
                    "urgent_flags": urgent_flags
                }
            )

            return result

        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            return ActionResult(
                success=False,
                outcome=DecisionOutcome.FAILURE,
                errors=[str(e)]
            )

    # ========================================================================
    # LLM INTEGRATION
    # ========================================================================

    def _build_clinical_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build clinical reasoning prompt for LLM

        Uses chain-of-thought prompting for better reasoning.
        """
        prompt = f"""You are an expert clinical decision support AI assistant. Analyze the following patient case and provide a differential diagnosis.

**PATIENT PRESENTATION:**
Chief Complaint: {data.get('chief_complaint', 'Unknown')}

**VITAL SIGNS:**
{json.dumps(data.get('vitals', {}), indent=2)}

**SYMPTOMS:**
{', '.join(data.get('symptoms', []))}

**MEDICAL HISTORY:**
{', '.join(data.get('medical_history', []))}

**CURRENT MEDICATIONS:**
{', '.join(data.get('current_medications', []))}

**LABORATORY RESULTS:**
{json.dumps(data.get('labs', {}), indent=2)}

**INSTRUCTIONS:**
1. Provide a differential diagnosis with 3-5 possible diagnoses ranked by probability
2. For each diagnosis, provide:
   - Diagnosis name
   - Probability (0-1)
   - Supporting evidence from the patient data
   - Key findings that support or refute this diagnosis

3. Recommend diagnostic tests or imaging studies
4. Suggest initial treatment approaches
5. Flag any critical findings requiring immediate action

**OUTPUT FORMAT (JSON):**
```json
{{
  "differential_diagnosis": [
    {{
      "diagnosis": "Acute Coronary Syndrome",
      "probability": 0.75,
      "supporting_evidence": ["elevated troponin", "chest pain", "risk factors"],
      "severity": "critical"
    }}
  ],
  "recommended_tests": [
    {{"test": "ECG", "urgency": "immediate", "reason": "..."}},
    {{"test": "Troponin serial", "urgency": "within 1 hour", "reason": "..."}}
  ],
  "treatment_suggestions": [
    {{"treatment": "Aspirin 325mg", "urgency": "immediate", "reason": "..."}},
    {{"treatment": "Cardiology consult", "urgency": "within 1 hour", "reason": "..."}}
  ],
  "critical_findings": ["elevated troponin with chest pain"],
  "confidence": 0.85,
  "reasoning": "Step-by-step clinical reasoning...",
  "knowledge_sources": ["AHA/ACC 2024 Guidelines"]
}}
```

Think step-by-step and provide evidence-based recommendations."""

        return prompt

    async def _query_llm(self, prompt: str) -> str:
        """
        Query LLM (GPT-4 or Claude)

        Tries GPT-4 first, falls back to Claude if available.
        """
        # Try GPT-4 first
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model=settings.openai_model_gpt4o,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert clinical decision support AI. "
                                       "Provide evidence-based, accurate diagnoses and recommendations."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.openai_temperature,
                    max_tokens=settings.openai_max_tokens,
                    response_format={"type": "json_object"}
                )

                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"OpenAI query failed: {str(e)}")

        # Fallback to Claude
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=settings.anthropic_max_tokens,
                    temperature=settings.anthropic_temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                return response.content[0].text

            except Exception as e:
                logger.error(f"Anthropic query failed: {str(e)}")
                raise

        raise RuntimeError("No LLM client available")

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response and validate

        Returns structured diagnosis data.
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            # Validate required fields
            required = ["differential_diagnosis", "recommended_tests", "confidence"]
            for field in required:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Structure output
            return {
                "differential_diagnosis": data["differential_diagnosis"],
                "recommended_tests": data.get("recommended_tests", []),
                "treatment_suggestions": data.get("treatment_suggestions", []),
                "recommended_medications": [
                    t.get("treatment") for t in data.get("treatment_suggestions", [])
                    if "medication" in t.get("treatment", "").lower()
                ],
                "confidence": float(data["confidence"]),
                "reasoning_steps": [data.get("reasoning", "")],
                "knowledge_sources": data.get("knowledge_sources", []),
                "explanation": data.get("reasoning", "")
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Return low-confidence default
            return {
                "differential_diagnosis": [],
                "recommended_tests": [],
                "treatment_suggestions": [],
                "recommended_medications": [],
                "confidence": 0.0,
                "reasoning_steps": ["Failed to parse LLM response"],
                "knowledge_sources": [],
                "explanation": f"Error parsing response: {str(e)}"
            }

    # ========================================================================
    # SAFETY CHECKS
    # ========================================================================

    def _check_drug_interactions(
        self,
        current_meds: List[str],
        new_meds: List[str]
    ) -> List[Dict[str, str]]:
        """
        Check for drug-drug interactions

        In production, would use:
        - RxNorm API
        - First Databank
        - Micromedex
        """
        warnings = []

        for current in current_meds:
            current_lower = current.lower()

            for new in new_meds:
                new_lower = new.lower()

                # Check simple interaction database
                for drug, interactions in self.medical_knowledge["drug_interactions"].items():
                    if drug in current_lower:
                        for interaction in interactions:
                            if interaction.lower() in new_lower:
                                warnings.append({
                                    "severity": "warning",
                                    "interaction": f"{current} + {new}",
                                    "description": f"Potential interaction between {current} and {new}",
                                    "recommendation": "Review with pharmacist"
                                })

        return warnings

    def _check_urgent_findings(self, parameters: Dict[str, Any]) -> List[str]:
        """
        Check for urgent/critical findings requiring immediate action

        Returns list of urgent flags.
        """
        urgent_flags = []

        # Check differential diagnoses for critical conditions
        for dx in parameters.get("differential_diagnosis", []):
            if dx.get("severity") == "critical" and dx.get("probability", 0) > 0.5:
                urgent_flags.append(
                    f"HIGH PROBABILITY CRITICAL CONDITION: {dx.get('diagnosis')} ({dx.get('probability')*100:.0f}%)"
                )

        # Check for immediate action tests
        for test in parameters.get("recommended_tests", []):
            if test.get("urgency") == "immediate":
                urgent_flags.append(
                    f"IMMEDIATE TEST REQUIRED: {test.get('test')}"
                )

        return urgent_flags


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_clinical_decision_agent() -> ClinicalDecisionAgent:
    """Create and return configured clinical decision agent"""
    return ClinicalDecisionAgent()
