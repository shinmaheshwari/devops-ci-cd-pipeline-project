import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402


def client():
    app.testing = True
    return app.test_client()


def test_index_returns_200():
    resp = client().get("/")
    assert resp.status_code == 200


def test_health_returns_ok():
    resp = client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_metrics_returns_text():
    resp = client().get("/metrics")
    assert resp.status_code == 200
    assert b"app_uptime_seconds" in resp.data
