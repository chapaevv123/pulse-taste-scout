# Pulse Taste Scout

## Tagline

Cultural intelligence for decisions that actually fit you.

## Inspiration

Most recommendation agents can write confidently but cannot distinguish cultural fit from a plausible generic guess. We wanted an agent that grounds a real-world choice in cross-domain taste evidence and shows exactly what changed because of that evidence.

## What it does

A user provides several public cultural seeds—a film, artist, brand, place, book, or aesthetic—plus a city and a real decision. Pulse Taste Scout resolves those seeds to Qloo entities, queries Qloo for cross-domain place affinities, critiques evidence quality, optionally performs one bounded refinement, and returns three transparent recommendations with limitations.

## How Qloo is used

Qloo is the product's entity resolver and recommendation source. Every displayed match must originate from a Qloo entity ID returned by `/search` and `/v2/insights`. The UI exposes resolved entities, returned cross-domain signals, source attribution, and uncertainty.

## Why Qloo is load-bearing

Without Qloo, Pulse Taste Scout cannot name culturally ranked matches. Its disclosed generic baseline can only suggest broad categories such as a central cultural district or a popular venue. Removing Qloo therefore changes the actual answer, not merely its wording.

## How the agent works

1. Structure the decision and taste seeds.
2. Resolve each seed through Qloo Search.
3. Query Qloo Insights with the combined entity signal and location.
4. Critique result count and evidence strength.
5. Run at most one narrower Qloo query when evidence is sparse.
6. Rank three Qloo-returned entities.
7. Explain the evidence, uncertainty, and generic counterfactual.

The interface displays concise decision summaries, not hidden chain-of-thought.

## Tech stack

Python 3.11+, FastAPI, HTTPX, Jinja, lightweight HTML/CSS/JavaScript, pytest, Qloo Search and Insights APIs.

## Challenges

The hackathon credential uses the event gateway rather than Qloo's production gateway. We also designed the system to fail visibly when Qloo is unavailable and to avoid turning aggregate affinity into unsupported personal or causal claims.

## Accomplishments

- Verified live authentication, entity resolution, and cross-domain Insights.
- Kept the credential exclusively server-side.
- Built a bounded multi-step workflow with critic and retry paths.
- Made Qloo-vs-generic degradation visible in the product.
- Preserved sanitized live evidence for deterministic parser tests.

## What we learned

Entity resolution is part of recommendation quality, not preprocessing trivia. Cross-domain affinity is most useful when its provenance and limitations remain visible, and counterfactual evaluation is a practical way to prove an API is load-bearing.

## What's next

Add more decision-specific target categories, freshness/availability partners for events, user-controlled diversity preferences, and aggregate opt-in evaluation of whether recommendations were useful.

## Judge test instructions

1. Open the public demo without signing in.
2. Choose a fixture or enter 2–6 public cultural seeds.
3. Add a city and concrete decision.
4. Run Scout and inspect Qloo-resolved entities and top matches.
5. Review the critic step, limitations, and “How Qloo changed this answer” panel.

## Links

PUBLIC_REPO_URL: TO BE ADDED AFTER OWNER-APPROVED PUBLICATION

LIVE_DEMO_URL: TO BE ADDED AFTER OWNER-APPROVED DEPLOYMENT
