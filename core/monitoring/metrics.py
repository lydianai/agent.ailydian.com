"""
Prometheus Metrics Exporter

Provides comprehensive metrics for monitoring:
- Request latency and throughput
- AI agent performance
- Database query performance
- Resource utilization
- Error rates
- Custom business metrics
"""

import time
import psutil
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    generate_latest,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# PROMETHEUS REGISTRY
# ============================================================================

# Create custom registry (allows multiple registries)
registry = CollectorRegistry()


# ============================================================================
# HTTP METRICS
# ============================================================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

http_request_size_bytes = Summary(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=registry,
)

http_response_size_bytes = Summary(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
    registry=registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
    registry=registry,
)


# ============================================================================
# AI AGENT METRICS
# ============================================================================

ai_agent_invocations_total = Counter(
    "ai_agent_invocations_total",
    "Total AI agent invocations",
    ["agent_name", "status"],
    registry=registry,
)

ai_agent_duration_seconds = Histogram(
    "ai_agent_duration_seconds",
    "AI agent execution duration",
    ["agent_name"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry,
)

ai_agent_confidence_score = Histogram(
    "ai_agent_confidence_score",
    "AI agent confidence score distribution",
    ["agent_name"],
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=registry,
)

ai_model_tokens_used = Counter(
    "ai_model_tokens_used_total",
    "Total tokens consumed by AI models",
    ["model_name", "agent_name"],
    registry=registry,
)


# ============================================================================
# CLINICAL METRICS
# ============================================================================

emergency_triage_total = Counter(
    "emergency_triage_total",
    "Total emergency triage assessments",
    ["esi_level", "emergency_type"],
    registry=registry,
)

protocol_activations_total = Counter(
    "protocol_activations_total",
    "Total time-critical protocol activations",
    ["protocol_name"],
    registry=registry,
)

patient_monitoring_alerts = Counter(
    "patient_monitoring_alerts_total",
    "Total patient monitoring alerts",
    ["alert_type", "severity"],
    registry=registry,
)

news2_score_distribution = Histogram(
    "news2_score_distribution",
    "Distribution of NEWS2 scores",
    buckets=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20),
    registry=registry,
)


# ============================================================================
# DATABASE METRICS
# ============================================================================

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query execution time",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry,
)

db_connections_active = Gauge(
    "db_connections_active",
    "Number of active database connections",
    registry=registry,
)

db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table", "status"],
    registry=registry,
)


# ============================================================================
# QUANTUM COMPUTING METRICS
# ============================================================================

quantum_jobs_total = Counter(
    "quantum_jobs_total",
    "Total quantum computing jobs",
    ["backend", "status"],
    registry=registry,
)

quantum_job_duration_seconds = Histogram(
    "quantum_job_duration_seconds",
    "Quantum job execution duration",
    ["backend"],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 1800.0),
    registry=registry,
)

quantum_circuit_depth = Histogram(
    "quantum_circuit_depth",
    "Quantum circuit depth distribution",
    buckets=(10, 50, 100, 200, 500, 1000, 2000, 5000),
    registry=registry,
)


# ============================================================================
# SYSTEM METRICS
# ============================================================================

system_cpu_usage_percent = Gauge(
    "system_cpu_usage_percent",
    "CPU usage percentage",
    registry=registry,
)

system_memory_usage_bytes = Gauge(
    "system_memory_usage_bytes",
    "Memory usage in bytes",
    registry=registry,
)

system_disk_usage_bytes = Gauge(
    "system_disk_usage_bytes",
    "Disk usage in bytes",
    ["mount_point"],
    registry=registry,
)

application_info = Info(
    "application",
    "Application information",
    registry=registry,
)


# ============================================================================
# ERROR METRICS
# ============================================================================

errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "component"],
    registry=registry,
)

exceptions_total = Counter(
    "exceptions_total",
    "Total exceptions",
    ["exception_class", "component"],
    registry=registry,
)


# ============================================================================
# BUSINESS METRICS
# ============================================================================

active_users_total = Gauge(
    "active_users_total",
    "Number of active users",
    ["hospital_id", "role"],
    registry=registry,
)

active_sessions_total = Gauge(
    "active_sessions_total",
    "Number of active sessions",
    registry=registry,
)

subscription_tier_distribution = Gauge(
    "subscription_tier_distribution",
    "Distribution of subscription tiers",
    ["tier"],
    registry=registry,
)


# ============================================================================
# PROMETHEUS MIDDLEWARE
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware for Prometheus Metrics

    Automatically tracks all HTTP requests and responses.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """Track request metrics"""

        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Extract method and path
        method = request.method
        endpoint = request.url.path

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Track request size
        if request.headers.get("content-length"):
            request_size = int(request.headers["content-length"])
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Track duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

            # Track response size
            if response.headers.get("content-length"):
                response_size = int(response.headers["content-length"])
                http_response_size_bytes.labels(method=method, endpoint=endpoint).observe(response_size)

            # Track total requests
            status = response.status_code
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

            return response

        except Exception as e:
            # Track errors
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
            http_requests_total.labels(method=method, endpoint=endpoint, status=500).inc()
            errors_total.labels(error_type="http_error", component="middleware").inc()
            exceptions_total.labels(exception_class=type(e).__name__, component="middleware").inc()
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


# ============================================================================
# SYSTEM METRICS COLLECTOR
# ============================================================================

def collect_system_metrics():
    """Collect system-level metrics (CPU, memory, disk)"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage_percent.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage_bytes.set(memory.used)

        # Disk usage
        disk = psutil.disk_usage("/")
        system_disk_usage_bytes.labels(mount_point="/").set(disk.used)

    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        errors_total.labels(error_type="metrics_collection", component="system").inc()


# ============================================================================
# DECORATOR FOR TRACKING AI AGENT PERFORMANCE
# ============================================================================

def track_agent_performance(agent_name: str):
    """
    Decorator to track AI agent performance metrics

    Usage:
        @track_agent_performance("Emergency Response Agent")
        async def triage_patient(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)

                # Track confidence if available
                if isinstance(result, dict) and "confidence" in result:
                    ai_agent_confidence_score.labels(agent_name=agent_name).observe(result["confidence"])

                return result

            except Exception as e:
                status = "error"
                errors_total.labels(error_type="agent_error", component=agent_name).inc()
                exceptions_total.labels(exception_class=type(e).__name__, component=agent_name).inc()
                raise

            finally:
                # Track duration
                duration = time.time() - start_time
                ai_agent_duration_seconds.labels(agent_name=agent_name).observe(duration)

                # Track total invocations
                ai_agent_invocations_total.labels(agent_name=agent_name, status=status).inc()

        return wrapper
    return decorator


# ============================================================================
# DECORATOR FOR TRACKING DATABASE QUERIES
# ============================================================================

def track_database_query(operation: str, table: str):
    """
    Decorator to track database query performance

    Usage:
        @track_database_query("SELECT", "users")
        async def get_user(user_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                status = "error"
                raise

            finally:
                # Track duration
                duration = time.time() - start_time
                db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)

                # Track total queries
                db_queries_total.labels(operation=operation, table=table, status=status).inc()

        return wrapper
    return decorator


# ============================================================================
# METRICS ENDPOINT HANDLER
# ============================================================================

def get_metrics() -> Response:
    """
    Generate Prometheus metrics export

    Returns:
        Response with metrics in Prometheus format
    """
    # Collect latest system metrics
    collect_system_metrics()

    # Generate metrics
    metrics_data = generate_latest(registry)

    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================================================
# APPLICATION INFO
# ============================================================================

def set_application_info(version: str, environment: str, build_date: str):
    """Set application information in metrics"""
    application_info.info({
        "version": version,
        "environment": environment,
        "build_date": build_date,
        "python_version": "3.11",
        "framework": "FastAPI",
    })


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def track_emergency_triage(esi_level: str, emergency_type: str):
    """Track emergency triage metrics"""
    emergency_triage_total.labels(esi_level=esi_level, emergency_type=emergency_type).inc()


def track_protocol_activation(protocol_name: str):
    """Track time-critical protocol activation"""
    protocol_activations_total.labels(protocol_name=protocol_name).inc()


def track_patient_alert(alert_type: str, severity: str):
    """Track patient monitoring alerts"""
    patient_monitoring_alerts.labels(alert_type=alert_type, severity=severity).inc()


def track_news2_score(score: int):
    """Track NEWS2 score distribution"""
    news2_score_distribution.observe(score)


def track_quantum_job(backend: str, duration: float, status: str, circuit_depth: int):
    """Track quantum computing job metrics"""
    quantum_jobs_total.labels(backend=backend, status=status).inc()
    quantum_job_duration_seconds.labels(backend=backend).observe(duration)
    quantum_circuit_depth.observe(circuit_depth)


def track_db_connections(active_count: int):
    """Track active database connections"""
    db_connections_active.set(active_count)


def track_active_users(hospital_id: str, role: str, count: int):
    """Track active users by hospital and role"""
    active_users_total.labels(hospital_id=hospital_id, role=role).set(count)


def track_active_sessions(count: int):
    """Track total active sessions"""
    active_sessions_total.set(count)


def track_subscription_tier(tier: str, count: int):
    """Track subscription tier distribution"""
    subscription_tier_distribution.labels(tier=tier).set(count)
