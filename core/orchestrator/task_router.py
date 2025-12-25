"""
Task Router

Intelligent task routing and load balancing for multi-agent system.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from queue import PriorityQueue
import logging

from .agent_registry import AgentRegistry, AgentInfo, AgentStatus

logger = logging.getLogger(__name__)


class TaskPriority(int, Enum):
    """Task priority levels"""
    CRITICAL = 1  # Life-threatening (sepsis, MI, stroke)
    URGENT = 2    # Urgent but not immediately life-threatening
    HIGH = 3      # Important, timely response needed
    MEDIUM = 4    # Routine with moderate urgency
    LOW = 5       # Background tasks, analytics


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task definition"""
    task_id: str
    task_type: str
    priority: TaskPriority
    required_capabilities: List[str]
    data: Dict[str, Any]

    # Assignment
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Metadata
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority.value < other.priority.value


class TaskRouter:
    """
    Intelligent task routing and load balancing

    Features:
    - Priority-based task assignment
    - Capability matching
    - Load balancing
    - Failover handling
    - Task queue management
    """

    def __init__(self, agent_registry: AgentRegistry):
        """
        Initialize task router

        Args:
            agent_registry: Agent registry instance
        """
        self.registry = agent_registry
        self.task_queue: PriorityQueue = PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.agent_tasks: Dict[str, List[str]] = {}  # agent_id -> task_ids

        # Routing strategies
        self.routing_strategies = {
            "round_robin": self._route_round_robin,
            "least_loaded": self._route_least_loaded,
            "fastest": self._route_fastest,
            "priority": self._route_by_priority,
        }

        self.default_strategy = "least_loaded"

        logger.info("Task Router initialized")

    async def submit_task(
        self,
        task_id: str,
        task_type: str,
        priority: TaskPriority,
        required_capabilities: List[str],
        data: Dict[str, Any],
        **kwargs
    ) -> Task:
        """
        Submit a new task for routing

        Args:
            task_id: Unique task identifier
            task_type: Type of task
            priority: Task priority
            required_capabilities: Required agent capabilities
            data: Task data payload
            **kwargs: Additional task properties

        Returns:
            Task object
        """
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            required_capabilities=required_capabilities,
            data=data,
            **kwargs
        )

        self.tasks[task_id] = task
        self.task_queue.put((priority.value, task_id, task))

        logger.info(
            f"Task submitted: {task_id} ({task_type}) - Priority: {priority.name}"
        )

        # Try to assign immediately
        await self.assign_pending_tasks()

        return task

    async def assign_pending_tasks(self, strategy: Optional[str] = None):
        """
        Assign pending tasks to available agents

        Args:
            strategy: Routing strategy to use
        """
        strategy = strategy or self.default_strategy
        router = self.routing_strategies.get(strategy, self._route_least_loaded)

        while not self.task_queue.empty():
            try:
                _, task_id, task = self.task_queue.get_nowait()

                # Skip if already assigned
                if task.status != TaskStatus.PENDING:
                    continue

                # Find suitable agent
                agent = await router(task)

                if agent:
                    await self._assign_task_to_agent(task, agent)
                else:
                    # No agent available, put back in queue
                    self.task_queue.put((task.priority.value, task_id, task))
                    logger.debug(f"No agent available for task {task_id}, requeueing")
                    break  # Stop processing for now

            except Exception as e:
                logger.error(f"Error assigning tasks: {e}")
                break

    async def _assign_task_to_agent(self, task: Task, agent: AgentInfo):
        """Assign a task to a specific agent"""
        task.assigned_agent_id = agent.agent_id
        task.assigned_at = datetime.utcnow()
        task.status = TaskStatus.ASSIGNED

        # Track agent tasks
        if agent.agent_id not in self.agent_tasks:
            self.agent_tasks[agent.agent_id] = []
        self.agent_tasks[agent.agent_id].append(task.task_id)

        # Update agent status
        await self.registry.update_agent(
            agent.agent_id,
            status=AgentStatus.BUSY,
            active_tasks=agent.active_tasks + 1
        )

        logger.info(f"Task {task.task_id} assigned to agent {agent.agent_id}")

    async def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        success: bool = True
    ):
        """
        Mark task as completed

        Args:
            task_id: Task identifier
            result: Task execution result
            success: Whether task succeeded
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.completed_at = datetime.utcnow()
        task.result = result
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        # Update agent
        if task.assigned_agent_id:
            agent = await self.registry.get_agent(task.assigned_agent_id)
            if agent:
                # Calculate response time
                if task.assigned_at:
                    response_time_ms = (
                        (task.completed_at - task.assigned_at).total_seconds() * 1000
                    )

                    # Update agent metrics
                    updates = {
                        "active_tasks": max(0, agent.active_tasks - 1),
                        "last_task_at": task.completed_at,
                    }

                    if success:
                        updates["tasks_completed"] = agent.tasks_completed + 1
                        updates["success_rate"] = (
                            (agent.tasks_completed * agent.success_rate + 100.0)
                            / (agent.tasks_completed + 1)
                        )
                    else:
                        updates["tasks_failed"] = agent.tasks_failed + 1
                        updates["success_rate"] = (
                            (agent.tasks_completed * agent.success_rate)
                            / (agent.tasks_completed + agent.tasks_failed + 1)
                        )

                    # Update average response time
                    if agent.avg_response_time_ms > 0:
                        updates["avg_response_time_ms"] = (
                            (agent.avg_response_time_ms * agent.tasks_completed + response_time_ms)
                            / (agent.tasks_completed + 1)
                        )
                    else:
                        updates["avg_response_time_ms"] = response_time_ms

                    await self.registry.update_agent(task.assigned_agent_id, **updates)

                # Update agent status to idle if no more tasks
                if agent.active_tasks <= 1:
                    await self.registry.update_agent(
                        task.assigned_agent_id,
                        status=AgentStatus.IDLE
                    )

            # Remove from agent tasks
            if task.assigned_agent_id in self.agent_tasks:
                self.agent_tasks[task.assigned_agent_id].remove(task_id)

        logger.info(f"Task {task_id} completed: success={success}")

    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.error = error
        await self.complete_task(task_id, {"error": error}, success=False)

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    async def get_agent_tasks(self, agent_id: str) -> List[Task]:
        """Get all tasks assigned to an agent"""
        task_ids = self.agent_tasks.get(agent_id, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]

    async def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        return [t for t in self.tasks.values() if t.status == status]

    # ========================================================================
    # ROUTING STRATEGIES
    # ========================================================================

    async def _route_round_robin(self, task: Task) -> Optional[AgentInfo]:
        """Round-robin routing"""
        agents = await self._find_capable_agents(task)
        if not agents:
            return None

        # Simple round-robin (in production, track last assigned)
        return agents[0]

    async def _route_least_loaded(self, task: Task) -> Optional[AgentInfo]:
        """Route to least loaded capable agent"""
        agents = await self._find_capable_agents(task)
        if not agents:
            return None

        # Find agent with fewest active tasks
        return min(agents, key=lambda a: a.active_tasks)

    async def _route_fastest(self, task: Task) -> Optional[AgentInfo]:
        """Route to fastest capable agent"""
        agents = await self._find_capable_agents(task)
        if not agents:
            return None

        # Find agent with lowest average response time
        agents_with_history = [a for a in agents if a.avg_response_time_ms > 0]
        if agents_with_history:
            return min(agents_with_history, key=lambda a: a.avg_response_time_ms)

        # Fallback to first available
        return agents[0]

    async def _route_by_priority(self, task: Task) -> Optional[AgentInfo]:
        """Route to highest priority capable agent"""
        agents = await self._find_capable_agents(task)
        if not agents:
            return None

        # Find highest priority agent
        return max(agents, key=lambda a: a.priority_level)

    async def _find_capable_agents(self, task: Task) -> List[AgentInfo]:
        """Find agents capable of handling the task"""
        if not task.required_capabilities:
            # No specific requirements, return all active agents
            return await self.registry.get_all_agents(active_only=True)

        # Find agents with all required capabilities
        capable_agents = []

        for capability in task.required_capabilities:
            agents = await self.registry.find_agents_by_capability(capability)
            if not capable_agents:
                capable_agents = agents
            else:
                # Intersection: agents with ALL required capabilities
                capable_agents = [
                    a for a in capable_agents
                    if a in agents
                ]

        # Filter by availability
        available_agents = [
            a for a in capable_agents
            if a.status in [AgentStatus.ACTIVE, AgentStatus.IDLE]
            and a.active_tasks < a.max_concurrent_tasks
        ]

        return available_agents

    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total_tasks = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        assigned = sum(1 for t in self.tasks.values() if t.status == TaskStatus.ASSIGNED)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)

        return {
            "total_tasks": total_tasks,
            "pending": pending,
            "assigned": assigned,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "queue_size": self.task_queue.qsize(),
        }
