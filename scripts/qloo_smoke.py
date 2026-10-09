from __future__ import annotations

import json
import sys
from pathlib import Path

from pulse_taste_scout.config import Settings
from pulse_taste_scout.qloo_client import QlooClient


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    settings = Settings.load(project / ".env")
    with QlooClient(settings) as qloo:
        entities = qloo.search("Blade Runner", "urn:entity:movie", take=3)
        if not entities:
            raise RuntimeError("REAL_ENTITY_LOOKUP=FAIL: Qloo returned no matching entities")
        recommendations = qloo.insights(
            target_type="urn:entity:place",
            entity_ids=[entities[0].entity_id],
            location="Berlin",
            take=3,
        )
        if not recommendations:
            raise RuntimeError("REAL_AFFINITY_QUERY=FAIL: Qloo returned no recommendations")
    if "--persist" in sys.argv:
        def safe_entity(item: dict) -> dict:
            properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
            return {
                "entity_id": str(item.get("entity_id") or item.get("id") or ""),
                "name": str(item.get("name") or properties.get("name") or ""),
                "type": str(item.get("type") or item.get("subtype") or ""),
            }
        fixture = {
            "fixture_version": 1,
            "source": "Qloo Taste AI live API; sanitized",
            "query": {"seed": "Blade Runner", "target_type": "urn:entity:place", "location": "Berlin"},
            "resolved_entities": [
                {"entity_id": item.entity_id, "name": item.name, "type": item.entity_type}
                for item in entities
            ],
            "recommendations": [safe_entity(item) for item in recommendations],
        }
        path = project / "tests" / "fixtures" / "qloo_blade_runner_berlin.sanitized.json"
        path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Deliberately emit status/counts only. Never serialize headers, settings, or raw payloads.
    print(json.dumps({
        "QLOO_API_CONNECTED": True,
        "REAL_ENTITY_LOOKUP": "PASS",
        "REAL_AFFINITY_QUERY": "PASS",
        "resolved_entity_count": len(entities),
        "recommendation_count": len(recommendations),
        "sanitized_fixture_persisted": "--persist" in sys.argv,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
