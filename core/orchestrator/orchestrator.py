"""
Task Agent Orchestrator

Central coordination system for all healthcare AI agents.
Implements the orchestration architecture described in TASK_AGENT_PLAN.md
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .agent_registry import AgentRegistry, AgentCategory, AgentStatus
from .task_router import TaskRouter, Task, TaskPriority, TaskStatus
from .message_bus import MessageBus, Message

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Central orchestrator for multi-agent healthcare system

    Architecture:
    ┌─────────────────────────────────────────────────┐
    │     ORCHESTRATOR (Central Coordinator)          │
    │  - Task routing & prioritization                │
    │  - Agent conflict resolution                    │
    │  - Resource allocation                          │
    │  - Performance monitoring                       │
    └─────────────────────────────────────────────────┘
                          ▼
          ┌───────────────┴───────────────┐
          ▼                               ▼
    ┌─────────────┐              ┌─────────────┐
    │  EMERGENCY  │              │  QUANTUM    │
    │   AGENTS    │              │  OPTIMIZER  │
    │  (1,2,8)    │              │   AGENT     │
    └─────────────┘              └─────────────┘
          ▼                               ▼
    ┌─────────────┐              ┌─────────────┐
    │  CLINICAL   │              │  RESEARCH   │
    │   AGENTS    │              │   AGENTS    │
    │  (3,4,5,9)  │              │   (6,10)    │
    └─────────────┘              └─────────────┘
    """

    def __init__(self):
        """Initialize orchestrator"""
        self.registry = AgentRegistry(heartbeat_timeout=60)
        self.router = TaskRouter(self.registry)
        self.message_bus = MessageBus(max_history=1000)

        # Orchestrator state
        self.running = False
        self.started_at: Optional[datetime] = None

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []

        logger.info("Task Orchestrator initialized")

    async def start(self):
        """Start orchestrator services"""
        if self.running:
            logger.warning("Orchestrator already running")
            return

        self.running = True
        self.started_at = datetime.utcnow()

        # Start registry
        await self.registry.start()

        # Register all agents from TASK_AGENT_PLAN.md
        await self._register_core_agents()

        # Start background tasks
        self._background_tasks.append(
            asyncio.create_task(self._task_assignment_loop())
        )
        self._background_tasks.append(
            asyncio.create_task(self._performance_monitoring_loop())
        )

        # Subscribe to events
        self._setup_event_handlers()

        logger.info("Task Orchestrator started")

    async def stop(self):
        """Stop orchestrator services"""
        self.running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Stop registry
        await self.registry.stop()

        logger.info("Task Orchestrator stopped")

    async def _register_core_agents(self):
        """Register the 10 core task agents from TASK_AGENT_PLAN.md"""
        core_agents = [
            {
                "agent_id": "quantum-optimizer",
                "name": "Quantum Resource Optimizer",
                "category": AgentCategory.QUANTUM,
                "capabilities": [
                    "or_scheduling",
                    "staff_rostering",
                    "bed_allocation",
                    "quantum_optimization"
                ],
                "priority_level": 8,
            },
            {
                "agent_id": "sepsis-prediction",
                "name": "Sepsis Prediction & Intervention",
                "category": AgentCategory.EMERGENCY,
                "capabilities": [
                    "vital_monitoring",
                    "sepsis_detection",
                    "early_warning",
                    "protocol_activation"
                ],
                "priority_level": 10,  # Highest priority
            },
            {
                "agent_id": "surgical-safety",
                "name": "Surgical Safety Checklist",
                "category": AgentCategory.CLINICAL,
                "capabilities": [
                    "checklist_verification",
                    "instrument_counting",
                    "patient_verification",
                    "computer_vision"
                ],
                "priority_level": 9,
            },
            {
                "agent_id": "radiology-reporting",
                "name": "Radiology Auto-Reporting",
                "category": AgentCategory.CLINICAL,
                "capabilities": [
                    "image_analysis",
                    "report_generation",
                    "critical_findings",
                    "dicom_processing"
                ],
                "priority_level": 7,
            },
            {
                "agent_id": "medication-reconciliation",
                "name": "Medication Reconciliation",
                "category": AgentCategory.CLINICAL,
                "capabilities": [
                    "drug_interaction",
                    "dose_checking",
                    "medication_history",
                    "patient_education"
                ],
                "priority_level": 8,
            },
            {
                "agent_id": "clinical-trial-matching",
                "name": "Clinical Trial Matching",
                "category": AgentCategory.RESEARCH,
                "capabilities": [
                    "eligibility_screening",
                    "trial_matching",
                    "patient_outreach",
                    "enrollment_tracking"
                ],
                "priority_level": 5,
            },
            {
                "agent_id": "readmission-prevention",
                "name": "Predictive Readmission Prevention",
                "category": AgentCategory.OPERATIONAL,
                "capabilities": [
                    "risk_scoring",
                    "followup_scheduling",
                    "patient_monitoring",
                    "care_coordination"
                ],
                "priority_level": 7,
            },
            {
                "agent_id": "outbreak-detector",
                "name": "Infectious Disease Outbreak Detector",
                "category": AgentCategory.EMERGENCY,
                "capabilities": [
                    "infection_surveillance",
                    "outbreak_detection",
                    "contact_tracing",
                    "isolation_protocols"
                ],
                "priority_level": 9,
            },
            {
                "agent_id": "mental-health-crisis",
                "name": "Mental Health Crisis Predictor",
                "category": AgentCategory.CLINICAL,
                "capabilities": [
                    "risk_assessment",
                    "crisis_detection",
                    "suicide_prevention",
                    "psychiatric_referral"
                ],
                "priority_level": 10,  # Highest priority
            },
            {
                "agent_id": "genomic-therapy",
                "name": "Genomic Therapy Recommender",
                "category": AgentCategory.RESEARCH,
                "capabilities": [
                    "genomic_analysis",
                    "therapy_matching",
                    "precision_medicine",
                    "outcome_prediction"
                ],
                "priority_level": 6,
            },
        ]

        for agent_config in core_agents:
            await self.registry.register_agent(**agent_config)

        logger.info(f"Registered {len(core_agents)} core agents")

    def _setup_event_handlers(self):
        """Setup event handlers for agent communication"""
        # Task events
        self.message_bus.subscribe("task.submitted", self._on_task_submitted)
        self.message_bus.subscribe("task.completed", self._on_task_completed)
        self.message_bus.subscribe("task.failed", self._on_task_failed)

        # Agent events
        self.message_bus.subscribe("agent.registered", self._on_agent_registered)
        self.message_bus.subscribe("agent.failed", self._on_agent_failed)

        logger.info("Event handlers configured")

    async def submit_task(
        self,
        task_type: str,
        priority: TaskPriority,
        required_capabilities: List[str],
        data: Dict[str, Any],
        **kwargs
    ) -> Task:
        """
        Submit a new task to the orchestrator

        Args:
            task_type: Type of task
            priority: Task priority
            required_capabilities: Required agent capabilities
            data: Task data
            **kwargs: Additional task properties

        Returns:
            Task object
        """
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = await self.router.submit_task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            required_capabilities=required_capabilities,
            data=data,
            **kwargs
        )

        # Publish event
        await self.message_bus.publish(
            topic="task.submitted",
            payload={"task_id": task_id, "task_type": task_type, "priority": priority.name},
            sender_id="orchestrator"
        )

        return task

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics"""
        agent_stats = await self.registry.get_agent_stats()
        routing_stats = await self.router.get_routing_stats()

        uptime_seconds = (
            (datetime.utcnow() - self.started_at).total_seconds()
            if self.started_at else 0
        )

        return {
            "status": "operational" if self.running else "stopped",
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "uptime_seconds": round(uptime_seconds, 2),
            "agent_stats": agent_stats,
            "routing_stats": routing_stats,
            "message_bus": {
                "topics": self.message_bus.get_topics(),
                "message_count": len(self.message_bus.message_history),
            }
        }

    async def get_agent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent agent activity"""
        messages = self.message_bus.get_message_history(limit=limit)

        activities = []
        for msg in reversed(messages):
            agent_id = msg.sender_id or "system"
            agent = await self.registry.get_agent(agent_id) if agent_id != "system" else None

            activities.append({
                "agent_id": agent_id,
                "agent_name": agent.name if agent else "System",
                "task": msg.payload.get("description", msg.topic),
                "timestamp": msg.timestamp.isoformat(),
                "topic": msg.topic,
            })

        return activities

    # ========================================================================
    # BACKGROUND TASKS
    # ========================================================================

    async def _task_assignment_loop(self):
        """Background task for continuous task assignment"""
        while self.running:
            try:
                await self.router.assign_pending_tasks()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in task assignment loop: {e}")
                await asyncio.sleep(5)

    async def _performance_monitoring_loop(self):
        """Background task for performance monitoring"""
        while self.running:
            try:
                # Monitor and log performance metrics
                stats = await self.get_orchestrator_status()
                logger.debug(f"Orchestrator stats: {stats['agent_stats']}")

                await asyncio.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    async def _on_task_submitted(self, message: Message):
        """Handle task submitted event"""
        logger.debug(f"Task submitted: {message.payload}")

    async def _on_task_completed(self, message: Message):
        """Handle task completed event"""
        logger.info(f"Task completed: {message.payload}")

    async def _on_task_failed(self, message: Message):
        """Handle task failed event"""
        logger.error(f"Task failed: {message.payload}")

    async def _on_agent_registered(self, message: Message):
        """Handle agent registered event"""
        logger.info(f"Agent registered: {message.payload}")

    async def _on_agent_failed(self, message: Message):
        """Handle agent failure event"""
        agent_id = message.payload.get("agent_id")
        logger.error(f"Agent {agent_id} failed")

        # Mark agent as error status
        if agent_id:
            await self.registry.update_agent(agent_id, status=AgentStatus.ERROR)

        # Reassign agent's tasks
        tasks = await self.router.get_agent_tasks(agent_id)
        for task in tasks:
            if task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                # Resubmit task
                task.status = TaskStatus.PENDING
                task.assigned_agent_id = None
                self.router.task_queue.put((task.priority.value, task.task_id, task))

                logger.info(f"Reassigned task {task.task_id} due to agent failure")
