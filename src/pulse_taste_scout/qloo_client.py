from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .config import Settings


class QlooError(RuntimeError):
    """Safe public error that never contains request headers or credentials."""


@dataclass(frozen=True)
class ResolvedEntity:
    entity_id: str
    name: str
    entity_type: str


class QlooClient:
    """Small server-side Qloo API client using the official X-Api-Key scheme."""

    def __init__(self, settings: Settings, *, timeout_seconds: float = 12.0) -> None:
        self._client = httpx.Client(
            base_url=settings.qloo_base_url,
            headers={"X-Api-Key": settings.qloo_api_key, "Accept": "application/json"},
            timeout=httpx.Timeout(timeout_seconds),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "QlooClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise QlooError("Qloo request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise QlooError(f"Qloo request failed with status {exc.response.status_code}") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise QlooError("Qloo request failed") from exc
        if not isinstance(data, dict):
            raise QlooError("Qloo returned an unexpected response")
        return data

    @staticmethod
    def entities(data: dict[str, Any]) -> list[dict[str, Any]]:
        results = data.get("results", data)
        if isinstance(results, list):
            entities = results
        elif isinstance(results, dict):
            entities = results.get("entities", [])
        else:
            entities = []
        return [item for item in entities if isinstance(item, dict)]

    def search(self, query: str, entity_type: str | None = None, *, take: int = 5) -> list[ResolvedEntity]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        params: dict[str, Any] = {"query": query.strip(), "take": take}
        if entity_type:
            params["type"] = entity_type
        data = self._get("/search", params)
        resolved: list[ResolvedEntity] = []
        for item in self.entities(data):
            entity_id = str(item.get("entity_id") or item.get("id") or "")
            name = str(item.get("name") or item.get("properties", {}).get("name") or "")
            kind = str(item.get("type") or item.get("entity_type") or entity_type or "urn:entity")
            if entity_id and name:
                resolved.append(ResolvedEntity(entity_id, name, kind))
        return resolved

    def resolve_seed(self, query: str, entity_types: list[str]) -> ResolvedEntity | None:
        matches = self.search(query, None, take=5)
        exact = next((item for item in matches if item.name.casefold() == query.casefold()), None)
        return exact or (matches[0] if matches else None)

    def insights(
        self,
        *,
        target_type: str,
        entity_ids: list[str],
        location: str | None = None,
        take: int = 10,
    ) -> list[dict[str, Any]]:
        clean_ids = [value.strip() for value in entity_ids if value.strip()]
        if not clean_ids:
            raise ValueError("at least one resolved Qloo entity is required")
        params: dict[str, Any] = {
            "filter.type": target_type,
            "signal.interests.entities": ",".join(clean_ids),
            "take": take,
            "feature.explainability": "true",
        }
        if location:
            params["filter.location.query"] = location.strip()
        return self.entities(self._get("/v2/insights", params))
