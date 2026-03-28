# Project Cheat Sheet

Quick reference for goals, decisions, and key details. Read this to get back up to speed.

## What Are We Building?

A web app for the **dev-workflows** engineering handbook that lets developers:

1. **Browse** — Read rendered markdown docs with section navigation
2. **Discuss** — Threaded comments on specific doc sections
3. **Propose changes** — Edit docs in-app, which creates a GitHub PR
4. **Review & merge** — Approve/request changes/merge PRs through the app
5. **Stay notified** — Push notifications when something needs attention

## Why?

- Validate the dev-workflows handbook by building a real app with it
- Create a collaborative platform for the handbook (going public eventually)
- Solve Steve's pain point: blocked processes with no notification reaching him
- Exercise the full stack: React+TS PWA, Python/FastAPI, PostgreSQL, CI/CD, Railway

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend | React + TypeScript PWA | AI-fluent, browser-first, push notifications on all platforms |
| Backend | Python 3.12 + FastAPI | Async, fast, great ecosystem |
| Database | PostgreSQL | Relational data, full-text search, boring and reliable |
| Auth (v1) | GitHub OAuth only | First users are developers; viewer auth is v2 |
| Content source | GitHub → webhook → DB | GitHub is truth; DB for fast reads and per-section features |
| Comments | Own DB | Full control, fast, per-section threading |
| PR review comments | GitHub API | Keeps review discussion tied to the actual PR |
| Deployment | Railway | No server management, auto-deploy, cheap for small apps |
| Repo structure | Monorepo | One PR per feature, one CI pipeline |
| State management | React Context + TanStack Query | Small app, no Redux needed |
| Markdown rendering | react-markdown (client-side) | Flexible, no server-side HTML generation |

## Architecture at a Glance

```
GitHub webhook → Backend syncs markdown → PostgreSQL
Frontend (PWA) → Backend API → PostgreSQL
Frontend → Backend → GitHub API (PRs, reviews, merges)
Backend → pywebpush → Push Service → Service Worker → Notification
```

## Source Repo

The content comes from: `stevemcgregory/dev-workflows` on GitHub
- 10 markdown docs in `docs/` directory
- No frontmatter, H1 title, H2/H3 sections, code blocks, tables
- Each doc ends with a "Scaling Checklist"

## Environments

| Environment | Backend | Frontend | Database |
|-------------|---------|----------|----------|
| Local dev | uvicorn :8000 | vite :5173 | Docker PostgreSQL :5432 |
| Production | Railway service | Railway service (nginx) | Railway managed Postgres |

## Quick Commands

```bash
make setup          # One-time local setup
make dev-backend    # Start API server
make dev-frontend   # Start frontend dev server
make test           # Run all tests
make lint           # Run all linters
```
