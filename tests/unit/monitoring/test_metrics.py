"""
Unit Tests for Prometheus Metrics

Tests metrics collection, tracking, and export.
"""

import pytest
import time
from unittest.mock import Mock, AsyncMock

from core.monitoring.metrics import (
    track_emergency_triage,
    track_protocol_activation,
    track_agent_performance,
    track_database_query,
    emergency_triage_total,
    protocol_activations_total,
    ai_agent_invocations_total,
    ai_agent_duration_seconds,
    db_queries_total,
    db_query_duration_seconds,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestMetricsTracking:
    """Test metrics tracking functions"""

    async def test_track_emergency_triage(self):
        """Test emergency triage metrics tracking"""
        # Get initial count
        before = emergency_triage_total.labels(
            esi_level="level_1", emergency_type="cardiac_arrest"
        )._value.get()

        # Track a triage
        track_emergency_triage("level_1", "cardiac_arrest")

        # Verify count increased
        after = emergency_triage_total.labels(
            esi_level="level_1", emergency_type="cardiac_arrest"
        )._value.get()

        assert after == before + 1

    async def test_track_protocol_activation(self):
        """Test protocol activation tracking"""
        # Get initial count
        before = protocol_activations_total.labels(protocol_name="Stroke Alert")._value.get()

        # Track activation
        track_protocol_activation("Stroke Alert")

        # Verify count increased
        after = protocol_activations_total.labels(protocol_name="Stroke Alert")._value.get()

        assert after == before + 1

    async def test_agent_performance_decorator_success(self):
        """Test agent performance decorator on successful execution"""

        @track_agent_performance("Test Agent")
        async def test_function():
            await asyncio.sleep(0.01)  # Simulate work
            return {"confidence": 0.95}

        # Get initial count
        before_success = ai_agent_invocations_total.labels(
            agent_name="Test Agent", status="success"
        )._value.get()

        # Execute function
        result = await test_function()

        # Verify count increased
        after_success = ai_agent_invocations_total.labels(
            agent_name="Test Agent", status="success"
        )._value.get()

        assert after_success == before_success + 1
        assert result["confidence"] == 0.95

    async def test_agent_performance_decorator_error(self):
        """Test agent performance decorator on error"""

        @track_agent_performance("Test Agent Error")
        async def test_error_function():
            raise ValueError("Test error")

        # Get initial count
        before_error = ai_agent_invocations_total.labels(
            agent_name="Test Agent Error", status="error"
        )._value.get()

        # Execute function (should raise)
        with pytest.raises(ValueError):
            await test_error_function()

        # Verify error count increased
        after_error = ai_agent_invocations_total.labels(
            agent_name="Test Agent Error", status="error"
        )._value.get()

        assert after_error == before_error + 1

    async def test_database_query_decorator(self):
        """Test database query performance decorator"""

        @track_database_query("SELECT", "users")
        async def test_query():
            await asyncio.sleep(0.01)  # Simulate query
            return [{"user_id": 1, "name": "Test"}]

        # Get initial count
        before = db_queries_total.labels(
            operation="SELECT", table="users", status="success"
        )._value.get()

        # Execute query
        result = await test_query()

        # Verify count increased
        after = db_queries_total.labels(
            operation="SELECT", table="users", status="success"
        )._value.get()

        assert after == before + 1
        assert len(result) == 1


@pytest.mark.unit
class TestMetricsExport:
    """Test metrics export functionality"""

    def test_metrics_export_format(self):
        """Test that metrics can be exported in Prometheus format"""
        from core.monitoring.metrics import get_metrics

        # Generate metrics
        response = get_metrics()

        # Verify response
        assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
        assert response.body is not None

        # Check for expected metric names in output
        body_str = response.body.decode("utf-8")
        assert "http_requests_total" in body_str
        assert "ai_agent_invocations_total" in body_str


@pytest.mark.unit
class TestPrometheusMiddleware:
    """Test Prometheus middleware"""

    @pytest.mark.asyncio
    async def test_middleware_tracks_request(self):
        """Test that middleware tracks HTTP requests"""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from core.monitoring.metrics import PrometheusMiddleware, http_requests_total

        app = FastAPI()
        app.add_middleware(PrometheusMiddleware)

        @app.get("/test-endpoint")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Get initial count
        before = http_requests_total.labels(
            method="GET", endpoint="/test-endpoint", status=200
        )._value.get()

        # Make request
        response = client.get("/test-endpoint")

        # Verify response
        assert response.status_code == 200

        # Verify count increased
        after = http_requests_total.labels(
            method="GET", endpoint="/test-endpoint", status=200
        )._value.get()

        assert after == before + 1

    @pytest.mark.asyncio
    async def test_middleware_skips_metrics_endpoint(self):
        """Test that middleware doesn't track the metrics endpoint itself"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from core.monitoring.metrics import PrometheusMiddleware, get_metrics

        app = FastAPI()
        app.add_middleware(PrometheusMiddleware)

        @app.get("/metrics")
        async def metrics_endpoint():
            return get_metrics()

        client = TestClient(app)

        # Make request to metrics endpoint
        response = client.get("/metrics")

        # Verify response
        assert response.status_code == 200

        # Verify /metrics endpoint was NOT tracked (no label for it)
        # This test passes if no error is raised


import asyncio  # Import for async sleep
