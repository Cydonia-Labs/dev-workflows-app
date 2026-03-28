# dev-workflows-app

A web app for browsing, discussing, and collaboratively improving the [dev-workflows](https://github.com/Cydonia-Labs/dev-workflows) engineering handbook.

## Features

- **Browse** — Rendered markdown docs with section navigation and deep linking
- **Discuss** — Threaded comments per doc section
- **Propose changes** — Edit docs in-app, submit as GitHub PRs
- **Review & merge** — Approve, request changes, and merge PRs through the app
- **Push notifications** — PWA notifications when something needs your attention

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite (PWA) |
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Auth | GitHub OAuth |
| Deployment | Railway |

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 22 (via nvm)
- Docker (for local PostgreSQL)
- A GitHub OAuth App (for auth — see setup docs)

### Setup

```bash
git clone <this-repo>
cd dev-workflows-app
make setup
```

Edit `.env` with your GitHub OAuth credentials, then:

```bash
# Terminal 1
make dev-backend

# Terminal 2
make dev-frontend
```

The app will be available at `http://localhost:5173`.

## Development

```bash
make test    # Run all tests
make lint    # Run all linters
make clean   # Remove all build artifacts and local database
```

See [CLAUDE.md](CLAUDE.md) for architecture details and coding standards.
See [ROADMAP.md](ROADMAP.md) for feature tracking.
See [CHEATSHEET.md](CHEATSHEET.md) for a quick project overview.

## License

MIT
