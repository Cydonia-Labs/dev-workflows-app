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

## Phase 3: Frontend — Browsing

- [ ] Vite + React + Router scaffolding
- [ ] AppShell (sidebar nav, top bar, responsive layout)
- [ ] AuthContext + GitHub OAuth login flow
- [ ] DocsListPage (browse all handbook docs)
- [ ] DocViewPage (render markdown, section anchors, table of contents)

## Phase 4: Frontend — Collaboration

- [ ] SectionComments (threaded comments per doc section)
- [ ] CommentComposer (markdown input with preview)
- [ ] ProposeChangePage (markdown editor, diff preview, PR submission)
- [ ] ChangesListPage (open PRs)
- [ ] ChangeDetailPage (diff viewer, review actions, merge)

## Phase 5: Notifications & PWA

- [ ] Push notification subscription flow (frontend + backend)
- [ ] Service worker (push display, click-to-navigate)
- [ ] NotificationBell (unread count badge)
- [ ] NotificationsPage (inbox)
- [ ] PWA manifest, icons, offline caching, install prompt

## Phase 6: Deployment

- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile (build → nginx)
- [ ] Railway project setup (backend, frontend, managed Postgres)
- [ ] GitHub OAuth app configuration (callback URL)
- [ ] GitHub webhook configuration (push events)
- [ ] VAPID key generation and configuration
- [ ] Smoke test full flow: browse → comment → propose change → review → merge → sync

## Future (v2)

- [ ] Polls (vote on proposed changes or practices)
- [ ] Full-text search across docs
- [ ] Inline diff viewer / "suggest edit" mode
- [ ] Non-GitHub viewer auth (email/password or magic link)
- [ ] Activity feed / changelog
- [ ] Mobile-optimized editor
