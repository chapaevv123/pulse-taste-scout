from __future__ import annotations

import json

from fastapi.testclient import TestClient

from pulse_taste_scout.app import app


def main() -> int:
    scenarios = [
        {"name": "case_1", "seeds": ["Blade Runner", "A24", "Burial", "Muji"], "city": "Berlin", "decision": "What cultural night fits this taste?"},
        {"name": "case_2", "seeds": ["Studio Ghibli", "Japanese ceramics", "indie bookstores", "vegetarian food"], "city": "Kyoto", "decision": "What should I do on a slow-travel weekend?"},
        {"name": "case_3", "seeds": ["Formula 1", "streetwear", "electronic music", "modern architecture"], "city": "Barcelona", "decision": "Which city experiences fit this mix?"},
    ]
    client = TestClient(app)
    results = []
    all_passed = True
    for scenario in scenarios:
        response = client.post("/api/scout", json={key: scenario[key] for key in ("seeds", "city", "decision")})
        data = response.json()
        passed = (
            response.status_code == 200
            and data.get("source") == "Qloo Taste AI"
            and len(data.get("resolved_entities", [])) > 0
            and len(data.get("recommendations", [])) == 3
            and (data.get("counterfactual") or {}).get("materially_changed") is True
        )
        all_passed = all_passed and passed
        results.append({
            "case": scenario["name"], "passed": passed, "status": response.status_code,
            "source": data.get("source"), "resolved_entity_count": len(data.get("resolved_entities", [])),
            "recommendation_count": len(data.get("recommendations", [])),
            "agent_step_count": len(data.get("agent_steps", [])),
            "counterfactual_changed": (data.get("counterfactual") or {}).get("materially_changed"),
        })
    print(json.dumps(results))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
