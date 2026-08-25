"""
Placeholder web app for the DevOps CI/CD capstone.

Deliberately minimal — the point of this project is the pipeline
around the app, not the app itself. Swap this out for a real app
later without changing anything else in the pipeline, as long as
you keep a GET /health endpoint returning 200 when healthy.
"""
import os
import time

from flask import Flask, jsonify

app = Flask(__name__)

START_TIME = time.time()
APP_VERSION = os.environ.get("APP_VERSION", "dev")

# Simple in-memory request counter, exposed via /metrics in a
# Prometheus-friendly text format. Swap for prometheus_client
# once Sprint 5 wires up real scraping if you want richer metrics.
REQUEST_COUNT = 0


@app.before_request
def _count_request():
    global REQUEST_COUNT
    REQUEST_COUNT += 1


@app.route("/")
def index():
    return jsonify(
        message="Hello from the capstone app",
        version=APP_VERSION,
    )


@app.route("/health")
def health():
    """Liveness/readiness probe target for Kubernetes (Sprint 4)."""
    return jsonify(status="ok", uptime_seconds=round(time.time() - START_TIME, 1)), 200


@app.route("/metrics")
def metrics():
    """Bare-bones Prometheus text exposition (Sprint 5)."""
    uptime = time.time() - START_TIME
    body = (
        "# HELP app_uptime_seconds Time since process start\n"
        "# TYPE app_uptime_seconds gauge\n"
        f"app_uptime_seconds {uptime:.2f}\n"
        "# HELP app_requests_total Total requests served\n"
        "# TYPE app_requests_total counter\n"
        f"app_requests_total {REQUEST_COUNT}\n"
    )
    return body, 200, {"Content-Type": "text/plain; version=0.0.4"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
