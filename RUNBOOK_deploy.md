# RUNBOOK — From Zero to Running (2025-09-05)

**Goal:** Get the site running today, then switch to documentation.

## Checklist
- [ ] Clean copy made
- [ ] `.env` created from `.env.example`
- [ ] `docker compose up --build` runs without crash
- [ ] Home page reachable on http://localhost:8000
- [ ] Minimal smoke test: home, login page, list of books, add-to-cart page loads
- [ ] GitHub repo created and code pushed

## Commands
```bash
cp .env.example .env
docker compose up --build
# Later
git init && git add . && git commit -m "Dockerized MVP"
git remote add origin <repo-url>
git push -u origin main
```
