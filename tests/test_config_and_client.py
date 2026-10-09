from __future__ import annotations

import os

import httpx
import pytest

from pulse_taste_scout.config import MissingQlooKey, Settings
from pulse_taste_scout.qloo_client import QlooClient, QlooError


def test_missing_key_error_does_not_contain_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QLOO_API_KEY", raising=False)
    with pytest.raises(MissingQlooKey, match="QLOO_API_KEY"):
        Settings.load()


def test_settings_reject_non_https(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QLOO_API_KEY", "test-value-never-logged")
    monkeypatch.setenv("QLOO_BASE_URL", "http://example.invalid")
    with pytest.raises(ValueError, match="HTTPS"):
        Settings.load()


def test_search_parses_entities_without_leaking_key(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-value-never-logged"
    settings = Settings(secret, "https://hackathon.api.qloo.com")
    client = QlooClient(settings)
    request = httpx.Request("GET", "https://hackathon.api.qloo.com/search")
    response = httpx.Response(200, request=request, json={"results": {"entities": [
        {"entity_id": "movie-1", "name": "Blade Runner", "type": "urn:entity:movie"}
    ]}})
    monkeypatch.setattr(client._client, "get", lambda *args, **kwargs: response)
    assert client.search("Blade Runner", "urn:entity:movie")[0].entity_id == "movie-1"
    assert secret not in repr(client.search("Blade Runner", "urn:entity:movie"))
    client.close()


def test_search_parses_hackathon_results_array(monkeypatch: pytest.MonkeyPatch) -> None:
    client = QlooClient(Settings("test-value-never-logged"))
    request = httpx.Request("GET", "https://hackathon.api.qloo.com/search")
    response = httpx.Response(200, request=request, json={"results": [
        {"entity_id": "movie-1", "name": "Blade Runner", "type": "urn:entity:movie"}
    ]})
    monkeypatch.setattr(client._client, "get", lambda *args, **kwargs: response)
    assert client.search("Blade Runner", "urn:entity:movie")[0].name == "Blade Runner"
    client.close()


def test_auth_failure_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-value-never-logged"
    client = QlooClient(Settings(secret))
    request = httpx.Request("GET", "https://hackathon.api.qloo.com/search")
    response = httpx.Response(401, request=request, json={"error": "unauthorized"})
    monkeypatch.setattr(client._client, "get", lambda *args, **kwargs: response)
    with pytest.raises(QlooError) as caught:
        client.search("Blade Runner", "urn:entity:movie")
    assert secret not in str(caught.value)
    assert "401" in str(caught.value)
    client.close()


def test_timeout_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    client = QlooClient(Settings("test-value-never-logged"))
    def timeout(*args: object, **kwargs: object) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")
    monkeypatch.setattr(client._client, "get", timeout)
    with pytest.raises(QlooError, match="timed out"):
        client.search("Blade Runner", "urn:entity:movie")
    client.close()


def test_empty_signals_do_not_call_qloo() -> None:
    client = QlooClient(Settings("test-value-never-logged"))
    with pytest.raises(ValueError, match="resolved Qloo entity"):
        client.insights(target_type="urn:entity:place", entity_ids=[])
    client.close()
