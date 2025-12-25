#!/usr/bin/env python3
"""
Task Agent Orchestrator - Demo Script

Demonstrates the orchestrator system with all 10 agents.
Shows task submission, routing, and monitoring.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import TaskOrchestrator, TaskPriority


async def demo_basic_operations():
    """Demo: Basic orchestrator operations"""
    print("=" * 80)
    print("🏥 LYDIAN HEALTHCARE AI - TASK ORCHESTRATOR DEMO")
    print("=" * 80)
    print()

    # Initialize orchestrator
    print("📋 Initializing orchestrator...")
    orchestrator = TaskOrchestrator()

    # Start services
    print("🚀 Starting orchestrator services...")
    await orchestrator.start()
    print("✅ Orchestrator started\n")

    # Display status
    status = await orchestrator.get_orchestrator_status()
    print(f"📊 ORCHESTRATOR STATUS:")
    print(f"   Status: {status['status']}")
    print(f"   Uptime: {status['uptime_seconds']:.1f}s")
    print(f"   Agents: {status['agent_stats']['total_agents']}")
    print(f"   Active: {status['agent_stats']['active']}")
    print(f"   Idle: {status['agent_stats']['idle']}")
    print()

    # List all agents
    agents = await orchestrator.registry.get_all_agents(active_only=True)
    print(f"🤖 REGISTERED AGENTS ({len(agents)}):")
    print()

    for i, agent in enumerate(agents, 1):
        print(f"   {i:2d}. {agent.name}")
        print(f"       ID: {agent.agent_id}")
        print(f"       Category: {agent.category.value.upper()}")
        print(f"       Status: {agent.status.value.upper()}")
        print(f"       Priority: {agent.priority_level}/10")
        print(f"       Capabilities: {', '.join(agent.capabilities)}")
        print()

    return orchestrator


async def demo_task_submission(orchestrator: TaskOrchestrator):
    """Demo: Task submission and routing"""
    print("=" * 80)
    print("📤 TASK SUBMISSION DEMO")
    print("=" * 80)
    print()

    # Scenario 1: Critical sepsis screening
    print("🚨 Scenario 1: CRITICAL - Sepsis Screening")
    print("-" * 40)

    task1 = await orchestrator.submit_task(
        task_type="sepsis_screening",
        priority=TaskPriority.CRITICAL,
        required_capabilities=["vital_monitoring", "sepsis_detection"],
        data={
            "patient_id": "P-12345",
            "vital_signs": {
                "temperature": 38.5,
                "heart_rate": 120,
                "respiratory_rate": 24,
                "blood_pressure": "90/60",
                "spo2": 92,
                "wbc": 15.2
            },
            "clinical_notes": "Patient presenting with fever, tachycardia, hypotension"
        },
        patient_id="P-12345"
    )

    print(f"   Task ID: {task1.task_id}")
    print(f"   Priority: {task1.priority.name}")
    print(f"   Status: {task1.status.value}")
    print(f"   Created: {task1.created_at.strftime('%H:%M:%S')}")
    print()

    # Wait for assignment
    await asyncio.sleep(0.5)

    # Scenario 2: Routine radiology report
    print("📸 Scenario 2: MEDIUM - Radiology Report Generation")
    print("-" * 40)

    task2 = await orchestrator.submit_task(
        task_type="radiology_report",
        priority=TaskPriority.MEDIUM,
        required_capabilities=["image_analysis", "report_generation"],
        data={
            "patient_id": "P-67890",
            "study_type": "chest_xray",
            "indication": "Cough, fever",
            "image_path": "/studies/2024/12/xray_12345.dcm"
        },
        patient_id="P-67890"
    )

    print(f"   Task ID: {task2.task_id}")
    print(f"   Priority: {task2.priority.name}")
    print(f"   Status: {task2.status.value}")
    print()

    # Scenario 3: Quantum OR scheduling
    print("⚛️  Scenario 3: HIGH - Quantum OR Schedule Optimization")
    print("-" * 40)

    task3 = await orchestrator.submit_task(
        task_type="or_scheduling",
        priority=TaskPriority.HIGH,
        required_capabilities=["or_scheduling", "quantum_optimization"],
        data={
            "date": "2025-12-26",
            "surgeries": [
                {"type": "cardiac", "duration_min": 180, "priority": "urgent"},
                {"type": "orthopedic", "duration_min": 90, "priority": "routine"},
                {"type": "neurosurgery", "duration_min": 240, "priority": "urgent"},
            ],
            "or_rooms": 3,
            "constraints": ["minimize_wait_time", "maximize_utilization"]
        }
    )

    print(f"   Task ID: {task3.task_id}")
    print(f"   Priority: {task3.priority.name}")
    print(f"   Status: {task3.status.value}")
    print()

    # Wait for routing
    await asyncio.sleep(1)

    # Show routing stats
    routing_stats = await orchestrator.router.get_routing_stats()
    print("📊 ROUTING STATISTICS:")
    print(f"   Total Tasks: {routing_stats['total_tasks']}")
    print(f"   Pending: {routing_stats['pending']}")
    print(f"   Assigned: {routing_stats['assigned']}")
    print(f"   Queue Size: {routing_stats['queue_size']}")
    print()


async def demo_agent_monitoring(orchestrator: TaskOrchestrator):
    """Demo: Agent monitoring and health checks"""
    print("=" * 80)
    print("🔍 AGENT MONITORING DEMO")
    print("=" * 80)
    print()

    # Simulate agent heartbeats
    print("💓 Simulating agent heartbeats...")
    agents = await orchestrator.registry.get_all_agents(active_only=True)

    for agent in agents[:5]:  # First 5 agents
        await orchestrator.registry.heartbeat(
            agent.agent_id,
            cpu_percent=15.5 + (hash(agent.agent_id) % 20),
            memory_mb=256.0 + (hash(agent.agent_id) % 200)
        )

    print("✅ Heartbeats sent\n")

    # Display agent statistics
    stats = await orchestrator.registry.get_agent_stats()

    print("📈 AGENT STATISTICS:")
    print(f"   Total Agents: {stats['total_agents']}")
    print(f"   Active: {stats['active']}")
    print(f"   Idle: {stats['idle']}")
    print(f"   Busy: {stats['busy']}")
    print(f"   Offline: {stats['offline']}")
    print(f"   Error: {stats['error']}")
    print(f"   Avg Success Rate: {stats['avg_success_rate']:.2f}%")
    print()

    # Find agents by capability
    print("🔎 CAPABILITY SEARCH:")
    print("-" * 40)

    sepsis_agents = await orchestrator.registry.find_agents_by_capability("sepsis_detection")
    print(f"   Agents with 'sepsis_detection': {len(sepsis_agents)}")
    for agent in sepsis_agents:
        print(f"      - {agent.name} ({agent.status.value})")
    print()

    quantum_agents = await orchestrator.registry.find_agents_by_capability("quantum_optimization")
    print(f"   Agents with 'quantum_optimization': {len(quantum_agents)}")
    for agent in quantum_agents:
        print(f"      - {agent.name} ({agent.status.value})")
    print()


async def demo_message_bus(orchestrator: TaskOrchestrator):
    """Demo: Message bus and events"""
    print("=" * 80)
    print("📨 MESSAGE BUS DEMO")
    print("=" * 80)
    print()

    # Subscribe to events
    events_received = []

    def event_handler(message):
        events_received.append(message)
        print(f"   📬 Event: {message.topic} from {message.sender_id}")

    orchestrator.message_bus.subscribe("demo.test", event_handler)

    # Publish test events
    print("📤 Publishing test events...")
    print()

    await orchestrator.message_bus.publish(
        topic="demo.test",
        payload={"message": "Test event 1"},
        sender_id="demo_script"
    )

    await orchestrator.message_bus.publish(
        topic="demo.test",
        payload={"message": "Test event 2", "priority": "high"},
        sender_id="demo_script"
    )

    await asyncio.sleep(0.1)

    print()
    print(f"✅ Received {len(events_received)} events")
    print()

    # Show message history
    history = orchestrator.message_bus.get_message_history(limit=5)
    print(f"📜 Recent Messages ({len(history)}):")
    for msg in history:
        print(f"   - {msg.topic} @ {msg.timestamp.strftime('%H:%M:%S')}")
    print()


async def main():
    """Run all demos"""
    try:
        # Basic operations
        orchestrator = await demo_basic_operations()

        # Task submission
        await demo_task_submission(orchestrator)

        # Agent monitoring
        await demo_agent_monitoring(orchestrator)

        # Message bus
        await demo_message_bus(orchestrator)

        # Final status
        print("=" * 80)
        print("🎉 DEMO COMPLETE - FINAL STATUS")
        print("=" * 80)
        print()

        final_status = await orchestrator.get_orchestrator_status()
        print(f"   Total Tasks Submitted: {final_status['routing_stats']['total_tasks']}")
        print(f"   Messages Published: {final_status['message_bus']['message_count']}")
        print(f"   Active Agents: {final_status['agent_stats']['active']}")
        print(f"   Uptime: {final_status['uptime_seconds']:.1f}s")
        print()

        # Stop orchestrator
        print("🛑 Stopping orchestrator...")
        await orchestrator.stop()
        print("✅ Orchestrator stopped")
        print()

        print("=" * 80)
        print("💚 All demos completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print()
    asyncio.run(main())
    print()
