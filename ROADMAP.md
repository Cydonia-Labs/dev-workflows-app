# Roadmap

Feature tracking for dev-workflows-app. Each phase builds on the previous and produces a runnable increment.

## Phase 1: Foundation

- [x] Architecture and specification
- [x] Repo scaffolding (monorepo structure, Makefile, docker-compose, CI, CLAUDE.md)
- [x] Backend foundation (FastAPI app, config, database, ORM models, Alembic migration)
- [x] Content sync pipeline (markdown parser, sync service, webhook endpoint, seed script)

## Phase 2: Core Backend

- [x] GitHub OAuth (login flow, JWT sessions, get_current_user dependency)
- [x] Documents API (list, get by slug, get section)
- [x] Comments API (CRUD, threading, resolve)
- [x] Changes API (propose PR, list PRs, get PR detail, submit review, merge)
- [x] Notifications API (list, mark read, push subscription management)
- [x] Webhook endpoint (GitHub push events → content sync)
- [x] Security hardening (token encryption, rate limiting, headers, input validation)
- [x] Auto-seed docs from GitHub on startup

## Phase 3: Frontend — Browsing

- [x] Vite + React + Router scaffolding
- [x] AppShell (sidebar nav, top bar, responsive layout)
- [x] AuthContext + GitHub OAuth login flow
- [x] DocsListPage (browse all handbook docs)
- [x] DocViewPage (render markdown, section anchors, table of contents)

## Phase 4: Frontend — Collaboration

- [ ] SectionComments (threaded comments per doc section)
- [ ] CommentComposer (markdown input with preview)
- [ ] ProposeChangePage (markdown editor, diff preview, PR submission)
- [ ] ChangesListPage (open PRs) — basic version exists, needs detail view
- [ ] ChangeDetailPage (diff viewer, review actions, merge)

## Phase 5: Notifications & PWA

- [ ] Push notification subscription flow (frontend + backend)
- [ ] Service worker (push display, click-to-navigate)
- [ ] NotificationBell (unread count badge)
- [ ] NotificationsPage (inbox) — basic version exists, needs mark-read
- [ ] PWA manifest, icons, offline caching, install prompt

## Phase 6: End-to-End Testing & Deployment

- [ ] Create temporary GitHub PAT for GITHUB_SEED_TOKEN (private repo testing)
- [ ] Create GitHub OAuth App under Cydonia-Labs org
- [ ] End-to-end test: seed → browse → comment → propose → review → merge → sync
- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile (build → nginx)
- [ ] Railway project setup (backend, frontend, managed Postgres)
- [ ] GitHub webhook configuration (push events)
- [ ] VAPID key generation and configuration
- [ ] Make dev-workflows repo public (after E2E testing passes)
- [ ] Smoke test production deployment

## Future (v2)

- [ ] Polls (vote on proposed changes or practices)
- [ ] Full-text search across docs
- [ ] Inline diff viewer / "suggest edit" mode
- [ ] Non-GitHub viewer auth (email/password or magic link)
- [ ] Activity feed / changelog
- [ ] Mobile-optimized editor
- [ ] cydonialabs.com website (new build, remote hosting)
