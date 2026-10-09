from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .agent import ScoutRequest, TasteScoutAgent
from .config import MissingQlooKey, Settings
from .qloo_client import QlooClient, QlooError

PACKAGE = Path(__file__).resolve().parent
PROJECT = PACKAGE.parents[1]
app = FastAPI(title="Pulse Taste Scout", version="0.1.0")
app.mount("/static", StaticFiles(directory=PACKAGE / "static"), name="static")
templates = Jinja2Templates(directory=PACKAGE / "templates")


class ScoutPayload(BaseModel):
    seeds: list[str] = Field(min_length=1, max_length=6)
    city: str = Field(min_length=2, max_length=80)
    decision: str = Field(min_length=5, max_length=300)


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "qloo": "server-side"}


@app.post("/api/scout")
def scout(payload: ScoutPayload) -> dict:
    try:
        settings = Settings.load(PROJECT / ".env")
        with QlooClient(settings) as client:
            return TasteScoutAgent(client).run(ScoutRequest(payload.seeds, payload.city, payload.decision))
    except MissingQlooKey as exc:
        raise HTTPException(503, "Qloo is not configured on the server") from exc
    except (QlooError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
