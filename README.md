# Pulse Taste Scout

**Cultural intelligence for decisions that actually fit you.**

Pulse Taste Scout is a standalone Qloo Agentic Hackathon project. It turns a small set of cultural taste seeds into cross-domain recommendations grounded by Qloo's taste graph. This repository currently contains the secure server-side Qloo client and live-integration smoke-test gate. The agent and product UI are intentionally gated on a successful real API call.

## The problem

General-purpose language models can produce plausible lists, but plausibility is not evidence of cultural fit. Pulse Taste Scout resolves a user's public cultural references through Qloo, uses their combined cross-domain affinity to rank real entities, and shows the provenance and limits of the result.

> Qloo resolves your taste signals into real cultural entities and cross-domain affinities. The agent uses those affinities to rank and explain recommendations that a generic LLM would otherwise guess.

## Security-first setup

Requirements: Python 3.11+.

```powershell
cd pulse-taste-scout
Copy-Item .env.example .env
```

Edit `.env` locally and set `QLOO_API_KEY`. Never paste the key into chat, source code, screenshots, issue trackers, browser JavaScript, or test fixtures. `.env` is ignored by Git. Hackathon credentials use `https://hackathon.api.qloo.com`, and authentication is sent server-side using a raw `X-Api-Key` value.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe .\scripts\qloo_smoke.py
.\.venv\Scripts\python.exe -m pytest
```

Run the product:

```powershell
.\.venv\Scripts\python.exe -m uvicorn pulse_taste_scout.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The browser calls only the same-origin `/api/scout` route. Qloo authentication and requests occur inside FastAPI.

The smoke script prints only pass/fail statuses and result counts. It does not persist or print raw responses, request headers, or secrets.

## Planned load-bearing flow

```text
Taste seeds + decision
  -> Qloo entity resolution
  -> Qloo cross-domain affinities
  -> candidate construction
  -> evidence critic / optional second Qloo query
  -> ranked recommendations
  -> concise evidence and uncertainty
  -> Qloo-enabled vs generic-baseline comparison
```

Qloo is load-bearing: recommendations must bind to resolved Qloo entity IDs and returned affinity evidence. If Qloo is unavailable, the product must disclose degradation rather than invent cultural affinities.

## Qloo endpoints

- `GET /search` resolves each public taste seed to a Qloo entity.
- `GET /v2/insights` ranks target entities from the combined entity signal and optional location filter.

Both calls use the 2026 hackathon gateway and a raw `X-Api-Key` header from the server environment. The key never reaches the browser.

## Architecture

```text
Browser (no secrets)
  -> FastAPI /api/scout
    -> intake + entity agent
      -> Qloo /search
    -> taste graph + candidate agent
      -> Qloo /v2/insights
    -> evidence critic (at most one retry)
    -> ranking + concise explanation
    -> Qloo result vs disclosed generic baseline
```

The generic baseline is deliberately incapable of producing named cultural-affinity matches. It exists to make the contribution of Qloo observable, not as a silent fallback.

## Deployment

The included `Dockerfile` and `render.yaml` are deployment-ready. After owner approval, create a public repository, connect it to Render, set `QLOO_API_KEY` as a secret server-side environment variable, and deploy. Do not put the key in `render.yaml` or any browser-prefixed variable.

```powershell
render deploy
```

After deployment, run a real fixture, inspect the browser bundle/network panel for secret absence, and verify `/health` and `/api/scout`. No external deployment has been performed from this workspace.

## Judge test flow

1. Choose one of the three scenarios or enter 2–6 public taste seeds.
2. Add a city/context and a concrete decision.
3. Run Scout and inspect the resolved Qloo entities.
4. Review the three Qloo-ranked matches, evidence, confidence, and limitations.
5. Open “How Qloo changed this answer” and compare it with the disclosed generic baseline.
6. Review the concise agent-step summary, including whether the critic triggered a bounded retry.

## Security and limitations

- Do not commit `.env`; use server-side secret storage in deployment.
- Qloo affinities are aggregate cultural signals, not personal facts or causal claims.
- A recommendation is a discovery lead, not proof of opening hours, ticket availability, safety, or current event schedules.
- The generic baseline is illustrative and does not establish scientific superiority.
- No hidden chain-of-thought is displayed or stored; the UI shows concise decision evidence only.

## Current hackathon gate

The 2026 rules require a working Qloo-powered agentic application, an externally hosted functional demo, a public open-source repository with a visible license and complete source/setup instructions, and an English description. Video is not required. Deadline: October 30, 2026 at 11:45 PM EDT (October 31 at 05:45 Europe/Kyiv).
