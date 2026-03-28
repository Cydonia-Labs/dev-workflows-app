# dev-workflows-app

## What This Project Does

A web app for browsing, discussing, and collaboratively improving the dev-workflows engineering handbook. Developers can view rendered markdown docs, comment on specific sections, propose changes (which create GitHub PRs), review and merge PRs — all through the app with push notifications.

## Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL
- **Frontend**: React 19, TypeScript, Vite, TanStack Query, react-markdown
- **Infrastructure**: Railway (backend + frontend + managed Postgres)
- **Integrations**: GitHub OAuth, GitHub REST API (PRs, branches, reviews), Web Push API

## Project Structure

```
dev-workflows-app/
├── backend/          # FastAPI API server
│   ├── src/          # Application code
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response models
│   │   ├── routers/  # FastAPI route handlers
│   │   ├── services/ # Business logic layer
│   │   └── github/   # GitHub API client
│   └── tests/        # pytest test suite
├── frontend/         # React PWA
│   └── src/
│       ├── api/       # API client functions
│       ├── contexts/  # React contexts (Auth, Notifications)
│       ├── hooks/     # TanStack Query wrappers
│       ├── pages/     # Route components
│       ├── components/ # Shared UI components
│       └── types/     # TypeScript interfaces
└── .github/workflows/ # CI pipeline
```

## Coding Standards

### Python
- Google-style docstrings (Args / Returns / Raises / Example)
- All public functions must have doc comments and unit tests
- ruff for linting and formatting
- pytest for tests, mirrors src/ structure under tests/

### TypeScript / React
- TSDoc for all exported functions and components
- Props interfaces named `<ComponentName>Props`
- Named exports only (no default exports)
- ESLint + Prettier for linting/formatting
- Vitest + React Testing Library for tests, co-located with source

### General
- No magic numbers — named constants with explanatory comments
- Explicit error handling, never swallow exceptions
- No TODO without explanation of what and why

## Common Commands

```bash
make setup          # Full local setup (Docker, Python venv, npm, migrations)
make dev-backend    # Start FastAPI dev server on :8000
make dev-frontend   # Start Vite dev server on :5173
make test           # Run all tests (pytest + vitest)
make lint           # Run all linters (ruff + prettier + eslint + tsc)
```

## Architecture Notes

- GitHub is the source of truth for doc content. The app syncs via webhook on merge to main.
- Documents are parsed into sections (H2/H3) at sync time for per-section comments and deep linking.
- All GitHub API calls use the authenticated user's OAuth token so actions are attributed to them.
- Push notifications via Web Push API + pywebpush. Service worker handles display and click-to-navigate.
- Auth is GitHub OAuth only (v1). Viewer auth deferred to v2.

## Environment Variables

See `.env.example` for the full list. Key ones:
- `DATABASE_URL` — PostgreSQL connection string
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` — OAuth app credentials
- `GITHUB_WEBHOOK_SECRET` — HMAC validation for webhooks
- `VAPID_PRIVATE_KEY` / `VAPID_PUBLIC_KEY` — Web Push signing keys
- `SECRET_KEY` — JWT signing key
