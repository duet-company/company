"""
Prometheus metrics for AI Data Labs platform.

Core metrics:
- API: request latency, total requests, errors
- Agents: active agents, agent requests, agent errors
- Database: connection pool size, query latency, query errors
- System: memory usage, CPU usage
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    start_http_server,
    REGISTRY,
)
import time
import psutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# API Metrics
API_REQUESTS_TOTAL = Counter(
    "aidatalabs_api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"]
)

API_REQUEST_DURATION = Histogram(
    "aidatalabs_api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf"))
)

API_REQUESTS_IN_PROGRESS = Gauge(
    "aidatalabs_api_requests_in_progress",
    "Current number of in-progress API requests",
    ["method", "endpoint"]
)

API_ERRORS_TOTAL = Counter(
    "aidatalabs_api_errors_total",
    "Total number of API errors",
    ["method", "endpoint", "error_type"]
)

# Agent Metrics
AGENTS_ACTIVE = Gauge(
    "aidatalabs_agents_active",
    "Number of active AI agents",
    ["agent_type"]
)

AGENT_REQUESTS_TOTAL = Counter(
    "aidatalabs_agent_requests_total",
    "Total number of agent requests",
    ["agent_type", "operation"]
)

AGENT_REQUEST_DURATION = Histogram(
    "aidatalabs_agent_request_duration_seconds",
    "Agent request duration in seconds",
    ["agent_type", "operation"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 30.0, 60.0, float("inf"))
)

AGENT_ERRORS_TOTAL = Counter(
    "aidatalabs_agent_errors_total",
    "Total number of agent errors",
    ["agent_type", "error_type"]
)

# Database Metrics
DB_CONNECTIONS_TOTAL = Gauge(
    "aidatalabs_db_connections_total",
    "Total number of database connections",
    ["database_type", "pool_name"]
)

DB_QUERY_DURATION = Histogram(
    "aidatalabs_db_query_duration_seconds",
    "Database query duration in seconds",
    ["database_type", "operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, float("inf"))
)

DB_QUERIES_TOTAL = Counter(
    "aidatalabs_db_queries_total",
    "Total number of database queries",
    ["database_type", "operation", "success"]
)

# System Metrics
SYSTEM_MEMORY_USAGE = Gauge(
    "aidatalabs_system_memory_bytes",
    "System memory usage in bytes"
)

SYSTEM_CPU_USAGE = Gauge(
    "aidatalabs_system_cpu_percent",
    "System CPU usage percentage"
)

SYSTEM_DISK_USAGE = Gauge(
    "aidatalabs_system_disk_bytes",
    "System disk usage in bytes",
    ["mountpoint"]
)

# Application Info
APP_INFO = Gauge(
    "aidatalabs_app_info",
    "Application information",
    ["version", "environment"]
)


class MetricsMiddleware:
    """FastAPI middleware to collect API metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        start_time = time.time()

        # Track in-progress requests
        method = request.method
        endpoint = self._get_endpoint(request)
        API_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            status_code = response.status_code
            API_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            API_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

            # Record errors for 4xx and 5xx
            if status_code >= 400:
                error_type = "client_error" if status_code < 500 else "server_error"
                API_ERRORS_TOTAL.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()

            return response
        except Exception as exc:
            # Record exception as error
            duration = time.time() - start_time
            API_ERRORS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                error_type=type(exc).__name__
            ).inc()
            raise
        finally:
            API_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

    def _get_endpoint(self, request):
        """Extract endpoint from request, sanitizing path params."""
        # For now, use the raw route path; could be improved to use route templates
        return request.url.path


def update_system_metrics():
    """Update system-level metrics."""
    # Memory
    memory = psutil.virtual_memory()
    SYSTEM_MEMORY_USAGE.set(memory.used)

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    SYSTEM_CPU_USAGE.set(cpu_percent)

    # Disk
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            SYSTEM_DISK_USAGE.labels(mountpoint=partition.mountpoint).set(usage.used)
        except Exception as e:
            logger.warning(f"Failed to get disk usage for {partition.mountpoint}: {e}")


def update_agent_metrics(agent_type: str, is_active: bool):
    """Update agent-related metrics."""
    # This would be called by agent lifecycle management
    key = f"agent_{agent_type}"
    current = AGENTS_ACTIVE.labels(agent_type=agent_type)
    if is_active:
        current.inc()
    else:
        current.dec()


def record_agent_request(agent_type: str, operation: str, duration: float, success: bool = True):
    """Record an agent request metric."""
    AGENT_REQUESTS_TOTAL.labels(agent_type=agent_type, operation=operation).inc()
    AGENT_REQUEST_DURATION.labels(agent_type=agent_type, operation=operation).observe(duration)

    if not success:
        AGENT_ERRORS_TOTAL.labels(agent_type=agent_type, error_type="execution_error").inc()


def record_db_query(database_type: str, operation: str, duration: float, success: bool = True):
    """Record database query metric."""
    DB_QUERIES_TOTAL.labels(
        database_type=database_type,
        operation=operation,
        success="success" if success else "error"
    ).inc()
    DB_QUERY_DURATION.labels(database_type=database_type, operation=operation).observe(duration)


def set_db_connections(database_type: str, pool_name: str, count: int):
    """Set current database connection count."""
    DB_CONNECTIONS_TOTAL.labels(database_type=database_type, pool_name=pool_name).set(count)


def setup_app_info(version: str, environment: str):
    """Set application info metrics."""
    APP_INFO.labels(version=version, environment=environment).set(1)


def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics HTTP server."""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


# Instrumentation helper decorators
def instrument_async(endpoint: str):
    """Decorator to instrument async endpoint with metrics."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = "UNKNOWN"  # Would need request context to get actual method

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                API_REQUESTS_TOTAL.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=200
                ).inc()
                API_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
                return result
            except Exception as exc:
                duration = time.time() - start_time
                API_ERRORS_TOTAL.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=type(exc).__name__
                ).inc()
                raise
        return wrapper
    return decorator