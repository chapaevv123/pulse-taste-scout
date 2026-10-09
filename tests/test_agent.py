from __future__ import annotations

from pulse_taste_scout.agent import ScoutRequest, TasteScoutAgent, generic_baseline
from pulse_taste_scout.qloo_client import QlooError, ResolvedEntity


class FakeQloo:
    def __init__(self, sparse: bool = False) -> None:
        self.calls = 0
        self.sparse = sparse

    def resolve_seed(self, query: str, entity_types: list[str]) -> ResolvedEntity | None:
        if query == "missing":
            return None
        return ResolvedEntity(f"id-{query}", query, entity_types[0])

    def insights(self, **kwargs):
        self.calls += 1
        count = 1 if self.sparse and self.calls == 1 else 3
        return [
            {"entity_id": f"place-{self.calls}-{i}", "name": f"Qloo Place {self.calls}-{i}", "type": "urn:entity:place", "tags": [{"name": "art space"}]}
            for i in range(count)
        ]


def request() -> ScoutRequest:
    return ScoutRequest(["Blade Runner", "Burial", "missing"], "Berlin", "Plan a cultural night")


def test_agent_is_multi_step_and_qloo_bound() -> None:
    result = TasteScoutAgent(FakeQloo()).run(request())
    assert [step["step"] for step in result["agent_steps"]] == ["INTAKE", "ENTITY AGENT", "TASTE GRAPH", "CRITIC", "RANKING", "EXPLANATION"]
    assert all(item["entity_id"].startswith("place-") for item in result["recommendations"])
    assert result["source"] == "Qloo Taste AI"


def test_critic_runs_one_bounded_retry() -> None:
    fake = FakeQloo(sparse=True)
    result = TasteScoutAgent(fake).run(request())
    assert fake.calls == 2
    assert next(step for step in result["agent_steps"] if step["step"] == "CRITIC")["status"] == "retried"


def test_counterfactual_materially_differs() -> None:
    result = TasteScoutAgent(FakeQloo()).run(request())
    baseline_names = {item["name"] for item in generic_baseline(request())}
    assert result["counterfactual"]["materially_changed"] is True
    assert not baseline_names.intersection(item["name"] for item in result["recommendations"])


def test_no_resolved_seed_fails_closed() -> None:
    req = ScoutRequest(["missing"], "Berlin", "Plan a cultural night")
    try:
        TasteScoutAgent(FakeQloo()).run(req)
    except QlooError as exc:
        assert "resolve" in str(exc)
    else:
        raise AssertionError("agent must fail without Qloo-resolved evidence")

