from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_zendesk_webhook_enqueues(monkeypatch):
    captured = {}

    def fake_enqueue(topic, payload, idempotency_key=None):
        captured["topic"] = topic
        captured["payload"] = payload
        captured["key"] = idempotency_key
        return "fake-uuid"

    import app.main as main_module
    monkeypatch.setattr(main_module, "enqueue", fake_enqueue)

    payload = {
        "ticket": {
            "id": 12345,
            "requester": {"email": "x@y.com"},
            "subject": "Troca",
            "description": "corpo",
        }
    }
    r = client.post("/webhooks/zendesk", json=payload)
    assert r.status_code == 200
    assert captured["topic"] == "triage.queue"
    assert captured["key"] == "zendesk-12345"


def test_zendesk_webhook_invalid_payload():
    r = client.post("/webhooks/zendesk", json={"foo": "bar"})
    assert r.status_code == 400