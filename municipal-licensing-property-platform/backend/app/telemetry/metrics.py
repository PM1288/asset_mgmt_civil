from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUESTS_TOTAL = Counter(
    "municipal_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY_SECONDS = Histogram(
    "municipal_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

BACKGROUND_TASKS_TOTAL = Counter(
    "municipal_background_tasks_total",
    "Total background task runs",
    ["task_name", "outcome"],
)


def metrics_response():
    return generate_latest(), CONTENT_TYPE_LATEST
