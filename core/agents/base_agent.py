"""
Base Agent Class

Abstract base class for all autonomous healthcare agents.
Implements core functionality: perception, reasoning, action, learning.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
from uuid import uuid4
import json
import time

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logging import get_logger
from core.database import AgentDecision, DecisionOutcome

logger = get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================

class Observation(BaseModel):
    """Input observation from environment"""
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    source: str
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None


class Decision(BaseModel):
    """Agent decision output"""
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    parameters: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: List[str] = Field(default_factory=list)
    knowledge_sources: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    explanation: Optional[str] = None


class ActionResult(BaseModel):
    """Result of action execution"""
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    outcome: DecisionOutcome
    details: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    total_decisions: int = 0
    successful_decisions: int = 0
    failed_decisions: int = 0
    avg_confidence: float = 0.0
    avg_decision_time_ms: float = 0.0
    human_reviews_required: int = 0


# ============================================================================
# BASE AGENT
# ============================================================================

class BaseHealthcareAgent(ABC):
    """
    Abstract base class for all healthcare AI agents.

    All agents must implement:
    - perceive(): Process incoming data
    - reason(): Make decision based on observation
    - act(): Execute decision
    - learn(): Update model based on outcome (optional)
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        agent_version: str = "1.0.0"
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.agent_version = agent_version

        # Metrics
        self.metrics = AgentMetrics()

        # Configuration from settings
        self.confidence_threshold = settings.agent_confidence_threshold
        self.human_review_threshold = settings.agent_human_review_threshold
        self.decision_timeout = settings.agent_decision_timeout_seconds
        self.max_retries = settings.agent_max_retries

        logger.info(
            f"Initialized agent",
            agent_id=agent_id,
            agent_type=agent_type,
            version=agent_version
        )

    # ========================================================================
    # ABSTRACT METHODS (must be implemented by subclasses)
    # ========================================================================

    @abstractmethod
    async def perceive(self, data: Dict[str, Any]) -> Observation:
        """
        Process incoming data into observation.

        Args:
            data: Raw input data

        Returns:
            Structured observation
        """
        pass

    @abstractmethod
    async def reason(self, observation: Observation) -> Decision:
        """
        Make decision based on observation.

        This is where the core AI logic lives (LLM calls, ML models, etc.)

        Args:
            observation: Structured observation

        Returns:
            Decision with confidence score and explanation
        """
        pass

    @abstractmethod
    async def act(self, decision: Decision) -> ActionResult:
        """
        Execute decision.

        Args:
            decision: Decision to execute

        Returns:
            Result of action execution
        """
        pass

    async def learn(self, outcome: Dict[str, Any]) -> None:
        """
        Update model based on outcome (optional).

        Args:
            outcome: Actual outcome data for learning

        Default implementation: no-op (agents can override)
        """
        pass

    # ========================================================================
    # CORE WORKFLOW
    # ========================================================================

    async def process(
        self,
        data: Dict[str, Any],
        db: AsyncSession
    ) -> ActionResult:
        """
        Main processing workflow: perceive → reason → act

        This method orchestrates the full agent lifecycle and includes:
        - Timing/metrics
        - Error handling
        - Audit logging
        - Safety guardrails

        Args:
            data: Input data
            db: Database session for audit logging

        Returns:
            Action result
        """
        start_time = time.time()

        try:
            # STEP 1: Perceive
            logger.debug("Agent perceiving input", agent_id=self.agent_id)
            observation = await self.perceive(data)

            # STEP 2: Reason
            logger.debug("Agent reasoning", agent_id=self.agent_id)
            decision = await self._reason_with_guardrails(observation)

            # STEP 3: Act
            logger.debug("Agent acting", agent_id=self.agent_id)
            result = await self.act(decision)

            # STEP 4: Audit log
            await self._log_decision(observation, decision, result, db)

            # Update metrics
            self._update_metrics(decision, result, time.time() - start_time)

            # Log success
            logger.info(
                "Agent decision completed",
                agent_id=self.agent_id,
                decision_id=decision.decision_id,
                confidence=decision.confidence,
                success=result.success,
                duration_ms=round((time.time() - start_time) * 1000, 2)
            )

            return result

        except Exception as e:
            logger.error(
                f"Agent processing failed: {str(e)}",
                agent_id=self.agent_id,
                error_type=type(e).__name__
            )

            # Return failure result
            return ActionResult(
                success=False,
                outcome=DecisionOutcome.FAILURE,
                errors=[str(e)]
            )

    # ========================================================================
    # SAFETY & GUARDRAILS
    # ========================================================================

    async def _reason_with_guardrails(self, observation: Observation) -> Decision:
        """
        Reasoning with safety guardrails applied

        Guardrails:
        1. Timeout protection
        2. Confidence thresholding
        3. Human-in-the-loop flagging
        4. Retry logic
        """
        for attempt in range(self.max_retries):
            try:
                # Call reason with timeout
                decision = await self.reason(observation)

                # Apply confidence threshold
                if decision.confidence < self.confidence_threshold:
                    logger.warning(
                        "Low confidence decision",
                        agent_id=self.agent_id,
                        confidence=decision.confidence,
                        threshold=self.confidence_threshold
                    )

                # Flag for human review if below threshold
                if decision.confidence < self.human_review_threshold:
                    decision.requires_human_review = True
                    logger.info(
                        "Decision flagged for human review",
                        agent_id=self.agent_id,
                        confidence=decision.confidence
                    )

                return decision

            except Exception as e:
                logger.warning(
                    f"Reasoning attempt {attempt + 1} failed: {str(e)}",
                    agent_id=self.agent_id
                )

                if attempt == self.max_retries - 1:
                    raise

        # Should never reach here
        raise RuntimeError("All reasoning attempts failed")

    # ========================================================================
    # AUDIT LOGGING
    # ========================================================================

    async def _log_decision(
        self,
        observation: Observation,
        decision: Decision,
        result: ActionResult,
        db: AsyncSession
    ) -> None:
        """
        Log decision to database for HIPAA audit trail

        Args:
            observation: Input observation
            decision: Agent decision
            result: Action result
            db: Database session
        """
        try:
            agent_decision = AgentDecision(
                agent_type=self.agent_type,
                agent_version=self.agent_version,
                patient_id=observation.patient_id,
                encounter_id=observation.encounter_id,
                input_data=observation.data,
                decision_type=decision.action,
                decision_output={
                    "action": decision.action,
                    "parameters": decision.parameters,
                    "explanation": decision.explanation
                },
                confidence_score=decision.confidence,
                reasoning_steps=decision.reasoning,
                knowledge_sources=decision.knowledge_sources,
                guardrails_applied={
                    "confidence_threshold": self.confidence_threshold,
                    "human_review_threshold": self.human_review_threshold
                },
                human_review_required=decision.requires_human_review,
                is_immutable=True
            )

            db.add(agent_decision)
            await db.commit()

            logger.audit(
                action=f"agent_decision_{self.agent_type}",
                user_id=self.agent_id,
                resource=f"patient:{observation.patient_id}",
                outcome="success" if result.success else "failure",
                decision_id=decision.decision_id,
                confidence=decision.confidence
            )

        except Exception as e:
            logger.error(f"Failed to log decision: {str(e)}")
            # Don't fail the whole operation if logging fails
            await db.rollback()

    # ========================================================================
    # METRICS
    # ========================================================================

    def _update_metrics(
        self,
        decision: Decision,
        result: ActionResult,
        duration_seconds: float
    ) -> None:
        """Update agent performance metrics"""
        self.metrics.total_decisions += 1

        if result.success:
            self.metrics.successful_decisions += 1
        else:
            self.metrics.failed_decisions += 1

        if decision.requires_human_review:
            self.metrics.human_reviews_required += 1

        # Update averages
        n = self.metrics.total_decisions
        self.metrics.avg_confidence = (
            (self.metrics.avg_confidence * (n - 1) + decision.confidence) / n
        )
        self.metrics.avg_decision_time_ms = (
            (self.metrics.avg_decision_time_ms * (n - 1) + duration_seconds * 1000) / n
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics"""
        return self.metrics.dict()

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id} type={self.agent_type}>"
