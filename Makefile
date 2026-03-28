.PHONY: setup dev-backend dev-frontend test lint clean

setup:
	@echo "Starting PostgreSQL..."
	docker compose up -d
	@echo "Setting up backend..."
	cd backend && python3.12 -m venv .venv
	cd backend && .venv/bin/pip install -e ".[dev]"
	cd backend && .venv/bin/alembic upgrade head
	@echo "Setting up frontend..."
	cd frontend && npm ci
	@test -f .env || cp .env.example .env
	@echo "Setup complete. Fill in .env then run 'make dev-backend' and 'make dev-frontend'."

dev-backend:
	cd backend && .venv/bin/uvicorn src.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest
	cd frontend && npx vitest run

lint:
	cd backend && .venv/bin/ruff check .
	cd backend && .venv/bin/ruff format --check .
	cd frontend && npx prettier --check .
	cd frontend && npx eslint .
	cd frontend && npx tsc --noEmit

clean:
	rm -rf backend/.venv backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
	docker compose down -v
