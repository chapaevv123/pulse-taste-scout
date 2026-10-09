# Architecture

```text
Public browser
  |  seeds + city + decision (no credential)
  v
FastAPI POST /api/scout
  |-- Intake: validate and structure the request
  |-- Entity agent: GET Qloo /search per seed
  |-- Taste graph: GET Qloo /v2/insights with resolved IDs
  |-- Critic: inspect evidence; permit at most one narrower retry
  |-- Ranking: retain only Qloo-returned entities
  |-- Explanation: provenance, confidence, and limitations
  `-- Counterfactual: named Qloo results vs disclosed generic categories
```

The Qloo credential exists only in the FastAPI process environment. The frontend receives resolved public entities and concise evidence, never request headers or hidden reasoning.
