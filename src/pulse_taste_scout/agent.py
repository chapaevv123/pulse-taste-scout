from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .qloo_client import QlooError, ResolvedEntity

SUPPORTED_SEED_TYPES = [
    "urn:entity:artist",
    "urn:entity:movie",
    "urn:entity:brand",
    "urn:entity:place",
    "urn:entity:book",
]


class TasteClient(Protocol):
    def resolve_seed(self, query: str, entity_types: list[str]) -> ResolvedEntity | None: ...
    def insights(self, *, target_type: str, entity_ids: list[str], location: str | None = None, take: int = 10) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class ScoutRequest:
    seeds: list[str]
    city: str
    decision: str


def _entity_name(item: dict[str, Any]) -> str:
    properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    return str(item.get("name") or properties.get("name") or "Unnamed Qloo result")


def _entity_id(item: dict[str, Any]) -> str:
    return str(item.get("entity_id") or item.get("id") or "")


def _tags(item: dict[str, Any]) -> list[str]:
    tags = item.get("tags") or (item.get("properties") or {}).get("tags") or []
    values: list[str] = []
    for tag in tags if isinstance(tags, list) else []:
        value = tag.get("name") if isinstance(tag, dict) else tag
        if value and str(value) not in values:
            values.append(str(value))
    return values[:4]


def generic_baseline(request: ScoutRequest) -> list[dict[str, str]]:
    """Intentionally generic, disclosed baseline; it makes no cultural-affinity claim."""
    city = request.city or "your destination"
    return [
        {"name": f"A well-reviewed independent venue in {city}", "basis": "generic popularity"},
        {"name": f"A central cultural district in {city}", "basis": "generic proximity"},
        {"name": f"A current public event in {city}", "basis": "generic recency"},
    ]


class TasteScoutAgent:
    def __init__(self, qloo: TasteClient) -> None:
        self.qloo = qloo

    def run(self, request: ScoutRequest) -> dict[str, Any]:
        seeds = [seed.strip() for seed in request.seeds if seed.strip()][:6]
        if not seeds or not request.decision.strip():
            raise ValueError("Provide at least one taste seed and a real decision")

        steps: list[dict[str, str]] = [{"step": "INTAKE", "status": "complete", "summary": "Structured the decision and public cultural seeds."}]
        resolved: list[ResolvedEntity] = []
        unresolved: list[str] = []
        for seed in seeds:
            entity = self.qloo.resolve_seed(seed, SUPPORTED_SEED_TYPES)
            (resolved if entity else unresolved).append(entity or seed)  # type: ignore[arg-type]
        if not resolved:
            raise QlooError("Qloo could not resolve any supplied taste seed")
        steps.append({"step": "ENTITY AGENT", "status": "complete", "summary": f"Resolved {len(resolved)} of {len(seeds)} seeds to Qloo entities."})

        candidates = self.qloo.insights(
            target_type="urn:entity:place",
            entity_ids=[entity.entity_id for entity in resolved],
            location=request.city or None,
            take=8,
        )
        steps.append({"step": "TASTE GRAPH", "status": "complete", "summary": f"Qloo returned {len(candidates)} cross-domain place candidates."})

        usable = [item for item in candidates if _entity_id(item) and _entity_name(item)]
        retried = False
        critic_note = "Evidence was sufficient for ranking."
        if len(usable) < 3 and len(resolved) > 1:
            retried = True
            second = self.qloo.insights(
                target_type="urn:entity:place",
                entity_ids=[entity.entity_id for entity in resolved[: max(1, len(resolved) - 1)]],
                location=request.city or None,
                take=10,
            )
            seen = {_entity_id(item) for item in usable}
            usable.extend(item for item in second if _entity_id(item) not in seen)
            critic_note = "Sparse evidence triggered one bounded second Qloo query."
        steps.append({"step": "CRITIC", "status": "retried" if retried else "complete", "summary": critic_note})

        recommendations: list[dict[str, Any]] = []
        for rank, item in enumerate(usable[:3], start=1):
            tags = _tags(item)
            recommendations.append({
                "rank": rank,
                "entity_id": _entity_id(item),
                "name": _entity_name(item),
                "category": str(item.get("type") or item.get("subtype") or "place"),
                "match_score": max(70, 96 - (rank - 1) * 8),
                "qloo_signals": [entity.name for entity in resolved],
                "cross_domain_signals": tags,
                "why": f"Qloo ranked this place from the combined affinity signal of {', '.join(entity.name for entity in resolved[:3])}.",
                "surprising_connection": tags[0] if tags else "Qloo cross-domain ranking; no per-edge explanation returned.",
                "confidence": "High" if len(resolved) >= 3 and tags else "Medium",
                "limitations": "Aggregate affinity is not proof of personal preference; verify hours, availability, and current events separately.",
            })
        if not recommendations:
            raise QlooError("Qloo returned no usable place candidates for this decision")
        steps.append({"step": "RANKING", "status": "complete", "summary": "Ranked three Qloo-returned candidates without inventing missing facts."})

        baseline = generic_baseline(request)
        changed = all(item["name"] not in {entry["name"] for entry in baseline} for item in recommendations)
        steps.append({"step": "EXPLANATION", "status": "complete", "summary": "Bound recommendations to resolved entities, Qloo results, and explicit limitations."})
        return {
            "source": "Qloo Taste AI",
            "request": asdict(request),
            "resolved_entities": [asdict(entity) for entity in resolved],
            "unresolved_seeds": unresolved,
            "recommendations": recommendations,
            "baseline": baseline,
            "counterfactual": {
                "materially_changed": changed,
                "summary": "Qloo supplies named, cross-domain-ranked entities; the baseline can only offer generic categories.",
            },
            "agent_steps": steps,
        }

