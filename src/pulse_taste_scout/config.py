from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_QLOO_BASE_URL = "https://hackathon.api.qloo.com"


class MissingQlooKey(RuntimeError):
    """Raised without echoing secret-bearing configuration."""


@dataclass(frozen=True)
class Settings:
    qloo_api_key: str
    qloo_base_url: str = DEFAULT_QLOO_BASE_URL

    @classmethod
    def load(cls, env_file: Path | None = None) -> "Settings":
        local: dict[str, str] = {}
        if env_file is not None and env_file.is_file():
            for raw_line in env_file.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                name = name.strip()
                if name in {"QLOO_API_KEY", "QLOO_BASE_URL"}:
                    local[name] = value.strip().strip('"').strip("'")
        key = os.getenv("QLOO_API_KEY", local.get("QLOO_API_KEY", "")).strip()
        if not key:
            raise MissingQlooKey("QLOO_API_KEY is not configured in the local environment")
        base_url = os.getenv(
            "QLOO_BASE_URL", local.get("QLOO_BASE_URL", DEFAULT_QLOO_BASE_URL)
        ).strip()
        if not base_url.startswith("https://"):
            raise ValueError("QLOO_BASE_URL must use HTTPS")
        return cls(qloo_api_key=key, qloo_base_url=base_url.rstrip("/"))
