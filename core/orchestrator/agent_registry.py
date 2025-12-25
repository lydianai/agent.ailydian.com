"""
Agent Registry

Manages registration, discovery, and lifecycle of all task agents.
"""

import asyncio
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent operational status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class AgentCategory(str, Enum):
    """Agent functional categories"""
    EMERGENCY = "emergency"
    CLINICAL = "clinical"
    QUANTUM = "quantum"
    RESEARCH = "research"
    OPERATIONAL = "operational"
    ANALYTICS = "analytics"


@dataclass
class AgentInfo:
    """Agent registration information"""
    agent_id: str
    name: str
    category: AgentCategory
    capabilities: List[str]
    status: AgentStatus = AgentStatus.OFFLINE
    version: str = "1.0.0"

    # Metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_response_time_ms: float = 0.0
    success_rate: float = 100.0

    # Lifecycle
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    last_task_at: Optional[datetime] = None

    # Resource usage
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    active_tasks: int = 0
    max_concurrent_tasks: int = 5

    # Configuration
    priority_level: int = 5  # 1-10, higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """
    Central registry for all task agents

    Features:
    - Agent registration and deregistration
    - Health monitoring via heartbeats
    - Capability-based discovery
    - Performance tracking
    - Automatic failover
    """

    def __init__(self, heartbeat_timeout: int = 60):
        """
        Initialize agent registry

        Args:
            heartbeat_timeout: Seconds before marking agent as offline
        """
        self.agents: Dict[str, AgentInfo] = {}
        self.capabilities_index: Dict[str, Set[str]] = defaultdict(set)
        self.category_index: Dict[AgentCategory, Set[str]] = defaultdict(set)
        self.heartbeat_timeout = heartbeat_timeout

        # Health monitoring
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info("Agent Registry initialized")

    async def start(self):
        """Start registry services"""
        if self._running:
            logger.warning("Registry already running")
            return

        self._running = True
        self._heartbeat_task = asyncio.create_task(self._monitor_heartbeats())
        logger.info("Agent Registry started")

    async def stop(self):
        """Stop registry services"""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent Registry stopped")

    async def register_agent(
        self,
        agent_id: str,
        name: str,
        category: AgentCategory,
        capabilities: List[str],
        **kwargs
    ) -> AgentInfo:
        """
        Register a new agent

        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            category: Agent category
            capabilities: List of agent capabilities
            **kwargs: Additional agent properties

        Returns:
            AgentInfo object
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered, updating...")
            return await self.update_agent(agent_id, status=AgentStatus.ACTIVE, **kwargs)

        agent_info = AgentInfo(
            agent_id=agent_id,
            name=name,
            category=category,
            capabilities=capabilities,
            status=AgentStatus.ACTIVE,
            **kwargs
        )

        # Store in registry
        self.agents[agent_id] = agent_info

        # Index by capabilities
        for capability in capabilities:
            self.capabilities_index[capability].add(agent_id)

        # Index by category
        self.category_index[category].add(agent_id)

        logger.info(f"Registered agent: {agent_id} ({name}) - Category: {category}")
        return agent_info

    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent

        Args:
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False

        agent_info = self.agents[agent_id]

        # Remove from capabilities index
        for capability in agent_info.capabilities:
            self.capabilities_index[capability].discard(agent_id)

        # Remove from category index
        self.category_index[agent_info.category].discard(agent_id)

        # Remove from registry
        del self.agents[agent_id]

        logger.info(f"Deregistered agent: {agent_id}")
        return True

    async def update_agent(self, agent_id: str, **updates) -> Optional[AgentInfo]:
        """
        Update agent information

        Args:
            agent_id: Agent identifier
            **updates: Fields to update

        Returns:
            Updated AgentInfo or None
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return None

        agent_info = self.agents[agent_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(agent_info, key):
                setattr(agent_info, key, value)

        # Update heartbeat
        agent_info.last_heartbeat = datetime.utcnow()

        return agent_info

    async def heartbeat(self, agent_id: str, **metrics) -> bool:
        """
        Agent heartbeat ping

        Args:
            agent_id: Agent identifier
            **metrics: Optional metrics to update

        Returns:
            True if successful
        """
        agent_info = await self.update_agent(agent_id, **metrics)

        if agent_info and agent_info.status == AgentStatus.OFFLINE:
            # Bring back online
            await self.update_agent(agent_id, status=AgentStatus.ACTIVE)
            logger.info(f"Agent {agent_id} back online")

        return agent_info is not None

    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information"""
        return self.agents.get(agent_id)

    async def find_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        Find agents with specific capability

        Args:
            capability: Required capability

        Returns:
            List of matching agents (active only)
        """
        agent_ids = self.capabilities_index.get(capability, set())
        return [
            self.agents[aid]
            for aid in agent_ids
            if self.agents[aid].status in [AgentStatus.ACTIVE, AgentStatus.IDLE]
        ]

    async def find_agents_by_category(self, category: AgentCategory) -> List[AgentInfo]:
        """
        Find agents by category

        Args:
            category: Agent category

        Returns:
            List of matching agents
        """
        agent_ids = self.category_index.get(category, set())
        return [self.agents[aid] for aid in agent_ids]

    async def get_all_agents(self, active_only: bool = False) -> List[AgentInfo]:
        """
        Get all registered agents

        Args:
            active_only: Return only active agents

        Returns:
            List of agents
        """
        agents = list(self.agents.values())

        if active_only:
            agents = [
                a for a in agents
                if a.status in [AgentStatus.ACTIVE, AgentStatus.IDLE, AgentStatus.BUSY]
            ]

        return agents

    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total = len(self.agents)
        active = sum(1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE)
        idle = sum(1 for a in self.agents.values() if a.status == AgentStatus.IDLE)
        busy = sum(1 for a in self.agents.values() if a.status == AgentStatus.BUSY)
        error = sum(1 for a in self.agents.values() if a.status == AgentStatus.ERROR)
        offline = sum(1 for a in self.agents.values() if a.status == AgentStatus.OFFLINE)

        total_tasks = sum(a.tasks_completed for a in self.agents.values())
        total_failed = sum(a.tasks_failed for a in self.agents.values())

        avg_success_rate = (
            sum(a.success_rate for a in self.agents.values()) / total
            if total > 0 else 100.0
        )

        return {
            "total_agents": total,
            "active": active,
            "idle": idle,
            "busy": busy,
            "error": error,
            "offline": offline,
            "total_tasks_completed": total_tasks,
            "total_tasks_failed": total_failed,
            "avg_success_rate": round(avg_success_rate, 2),
        }

    async def _monitor_heartbeats(self):
        """Background task to monitor agent heartbeats"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_timeout / 2)

                now = datetime.utcnow()
                timeout_delta = timedelta(seconds=self.heartbeat_timeout)

                for agent_id, agent_info in list(self.agents.items()):
                    # Skip offline agents
                    if agent_info.status == AgentStatus.OFFLINE:
                        continue

                    # Check heartbeat timeout
                    if now - agent_info.last_heartbeat > timeout_delta:
                        logger.warning(
                            f"Agent {agent_id} missed heartbeat, marking as offline"
                        )
                        agent_info.status = AgentStatus.OFFLINE

            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
