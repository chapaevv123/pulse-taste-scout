# Owner publication runbook

No command in this document has been executed against an external service.

## 1. Rotate the compromised credential

Obtain a replacement Qloo hackathon key and update only the local `.env`. Verify locally with:

```powershell
.\.venv\Scripts\python.exe .\scripts\qloo_smoke.py
```

## 2. Create the standalone Git repository

From the standalone project root:

```powershell
git init
git status --short --ignored
git add .
git status --short
git commit -m "Build Pulse Taste Scout for Qloo Agentic Hackathon"
git branch -M main
git remote add origin https://github.com/chapaevv123/pulse-taste-scout.git
git push -u origin main
```

Before `git commit`, confirm `.env`, `.venv`, `node_modules`, caches, and `*.egg-info` appear only as ignored files and no unrelated Pulse paths are staged.

Repository creation at `https://github.com/chapaevv123/pulse-taste-scout` must be completed by the owner before adding the remote or pushing.

## 3. Deploy on Render

1. In Render, create a Blueprint/Web Service from `chapaevv123/pulse-taste-scout`.
2. Render will read `render.yaml` and build the included Dockerfile.
3. Add `QLOO_API_KEY` as a secret environment variable. Never place its value in the repository.
4. Confirm `QLOO_BASE_URL=https://hackathon.api.qloo.com`.
5. Deploy and wait for `/health` to return `200`.
6. Run all three scenarios through the public UI.
7. Inspect the browser bundle and network responses to confirm the credential is absent.
8. Add the resulting public URL to `submission/DEVPOST.md`.

## 4. Final Devpost gate

Add the public repository and live-demo URLs, confirm the repository license is visible, test judge access in a private browser window, and submit through Devpost only after explicit owner approval.
