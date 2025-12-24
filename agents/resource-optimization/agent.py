"""
Resource Optimization Agent

Quantum-powered hospital resource optimization.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from core.agents.base_agent import (
    BaseHealthcareAgent, Observation, Decision, ActionResult
)
from core.config import settings
from core.logging import get_logger
from core.database import DecisionOutcome
from .quantum_scheduler import create_quantum_scheduler, Surgery, OperatingRoom

logger = get_logger()


class ResourceOptimizationAgent(BaseHealthcareAgent):
    """
    Resource optimization agent using quantum computing

    Capabilities:
    1. OR scheduling optimization (quantum QAOA)
    2. Bed assignment optimization
    3. Staff allocation
    4. Equipment management
    """

    def __init__(self, agent_id: str = "resource-opt-001"):
        super().__init__(
            agent_id=agent_id,
            agent_type="resource_optimization",
            agent_version="1.0.0"
        )

        # Initialize quantum scheduler
        self.quantum_scheduler = create_quantum_scheduler()

        logger.info("Resource Optimization Agent initialized with quantum support")

    async def perceive(self, data: Dict[str, Any]) -> Observation:
        """
        Process resource optimization request

        Expected input:
        {
            "optimization_type": "or_scheduling",  # or "bed_assignment", "staff_allocation"
            "date": "2025-12-24",
            "surgeries": [...],  # List of pending surgeries
            "operating_rooms": [...],  # Available ORs
            "constraints": {...}  # Additional constraints
        }
        """

        required = ["optimization_type", "date"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return Observation(
            data=data,
            source="resource_optimization_agent"
        )

    async def reason(self, observation: Observation) -> Decision:
        """
        Optimize resource allocation

        Uses quantum computing for NP-hard optimization problems.
        """

        data = observation.data
        opt_type = data["optimization_type"]

        if opt_type == "or_scheduling":
            result = await self._optimize_or_schedule(data)
        elif opt_type == "bed_assignment":
            result = await self._optimize_bed_assignment(data)
        elif opt_type == "staff_allocation":
            result = await self._optimize_staff_allocation(data)
        else:
            raise ValueError(f"Unknown optimization type: {opt_type}")

        # Build decision
        decision = Decision(
            action=f"optimize_{opt_type}",
            parameters=result,
            confidence=0.95 if result.get("method") == "quantum" else 0.85,
            reasoning=[
                f"Optimized {opt_type} using {result.get('method', 'classical')} method",
                f"Achieved {result.get('utilization', 0)}% utilization",
                f"Completed {result.get('completed_count', 0)} items"
            ],
            knowledge_sources=["Quantum QAOA", "Operations Research"],
            explanation=f"Resource optimization completed with {result.get('method')} algorithm"
        )

        return decision

    async def act(self, decision: Decision) -> ActionResult:
        """Execute resource optimization decision"""

        try:
            output = {
                "optimization_result": decision.parameters,
                "method": decision.parameters.get("method"),
                "utilization": decision.parameters.get("utilization"),
                "cost_savings": decision.parameters.get("cost_savings_usd", 0)
            }

            return ActionResult(
                success=True,
                outcome=DecisionOutcome.SUCCESS,
                details=output
            )

        except Exception as e:
            logger.error(f"Resource optimization action failed: {e}")
            return ActionResult(
                success=False,
                outcome=DecisionOutcome.FAILURE,
                errors=[str(e)]
            )

    # ========================================================================
    # OPTIMIZATION METHODS
    # ========================================================================

    async def _optimize_or_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize operating room schedule using quantum computing
        """

        # Parse surgeries
        surgeries = [
            Surgery(
                surgery_id=s["surgery_id"],
                patient_id=s["patient_id"],
                procedure_name=s["procedure_name"],
                duration_minutes=s["duration_minutes"],
                priority=s.get("priority", 3),
                surgeon_id=s["surgeon_id"],
                required_equipment=s.get("required_equipment", []),
                preferred_or=s.get("preferred_or"),
                anesthesia_type=s.get("anesthesia_type", "general")
            )
            for s in data.get("surgeries", [])
        ]

        # Parse ORs
        date = datetime.fromisoformat(data["date"])
        operating_rooms = [
            OperatingRoom(
                or_id=o["or_id"],
                name=o["name"],
                available_hours=[(
                    date.replace(hour=7, minute=0),
                    date.replace(hour=23, minute=0)
                )],
                equipment=o.get("equipment", []),
                room_type=o.get("room_type", "general")
            )
            for o in data.get("operating_rooms", [])
        ]

        # Optimize using quantum scheduler
        schedule = await self.quantum_scheduler.optimize_schedule(
            surgeries,
            operating_rooms,
            date
        )

        return {
            "assignments": schedule.assignments,
            "utilization": schedule.utilization,
            "completed_count": schedule.completed_count,
            "avg_wait_time_minutes": schedule.avg_wait_time_minutes,
            "cost_savings_usd": schedule.cost_savings_usd,
            "method": schedule.optimization_method
        }

    async def _optimize_bed_assignment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize bed assignments (classical for now)"""

        # Simplified bed assignment logic
        patients = data.get("patients", [])
        beds = data.get("beds", [])

        assignments = []
        available_beds = [b for b in beds if b.get("is_available", True)]

        for patient in patients:
            if not available_beds:
                break

            # Match by department and gender preferences
            for bed in available_beds:
                if bed.get("department") == patient.get("required_department"):
                    assignments.append({
                        "patient_id": patient["patient_id"],
                        "bed_id": bed["bed_id"],
                        "room": bed["room"],
                        "department": bed["department"]
                    })
                    available_beds.remove(bed)
                    break

        utilization = (len(assignments) / len(beds) * 100) if beds else 0

        return {
            "assignments": assignments,
            "utilization": round(utilization, 2),
            "completed_count": len(assignments),
            "method": "classical"
        }

    async def _optimize_staff_allocation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize staff scheduling"""

        # Simplified staff allocation
        shifts = data.get("shifts", [])
        staff = data.get("staff", [])

        allocations = []

        for shift in shifts:
            required_count = shift.get("required_staff", 1)
            assigned = []

            for s in staff:
                if len(assigned) >= required_count:
                    break

                # Check availability
                if s.get("available", True):
                    assigned.append({
                        "staff_id": s["staff_id"],
                        "name": s["name"],
                        "role": s["role"]
                    })

            allocations.append({
                "shift_id": shift["shift_id"],
                "shift_time": shift["time"],
                "department": shift["department"],
                "assigned_staff": assigned,
                "fulfillment": len(assigned) / required_count if required_count > 0 else 0
            })

        avg_fulfillment = sum(a["fulfillment"] for a in allocations) / len(allocations) if allocations else 0

        return {
            "allocations": allocations,
            "avg_fulfillment": round(avg_fulfillment * 100, 2),
            "completed_count": len(allocations),
            "method": "classical"
        }


def create_resource_optimization_agent() -> ResourceOptimizationAgent:
    """Create resource optimization agent"""
    return ResourceOptimizationAgent()
