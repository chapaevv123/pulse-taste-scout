from fastapi.testclient import TestClient

from pulse_taste_scout.app import app


def test_landing_explains_qloo_and_counterfactual() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "PULSE × QLOO TASTE AI" in response.text
    assert "a generic LLM would otherwise guess" in response.text


def test_health_never_exposes_configuration() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    text = response.text
    assert "QLOO_API_KEY" not in text
    assert "hack_" not in text


def test_invalid_input_rejected_before_api() -> None:
    response = TestClient(app).post("/api/scout", json={"seeds": [], "city": "B", "decision": "no"})
    assert response.status_code == 422
