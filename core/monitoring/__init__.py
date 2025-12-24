"""
Monitoring Module

Provides Prometheus metrics, health checks, and observability.
"""

from core.monitoring.metrics import (
    PrometheusMiddleware,
    get_metrics,
    set_application_info,
    track_agent_performance,
    track_database_query,
    track_emergency_triage,
    track_protocol_activation,
    track_patient_alert,
    track_news2_score,
    track_quantum_job,
    track_db_connections,
    track_active_users,
    track_active_sessions,
    track_subscription_tier,
    registry,
)

__all__ = [
    "PrometheusMiddleware",
    "get_metrics",
    "set_application_info",
    "track_agent_performance",
    "track_database_query",
    "track_emergency_triage",
    "track_protocol_activation",
    "track_patient_alert",
    "track_news2_score",
    "track_quantum_job",
    "track_db_connections",
    "track_active_users",
    "track_active_sessions",
    "track_subscription_tier",
    "registry",
]
