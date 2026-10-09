import json
from pathlib import Path


def test_live_fixture_is_sanitized_and_evidence_bearing() -> None:
    path = Path(__file__).parent / "fixtures" / "qloo_blade_runner_berlin.sanitized.json"
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    assert data["source"] == "Qloo Taste AI live API; sanitized"
    assert data["resolved_entities"]
    assert data["recommendations"]
    lowered = text.casefold()
    assert "api_key" not in lowered
    assert "x-api-key" not in lowered
    assert "authorization" not in lowered

