"""FastAPI application factory and startup configuration.

This is the entry point for the backend API. Uvicorn loads this module
to serve the application.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database import async_session_factory
from src.github.client import GitHubClient
from src.middleware.rate_limit import RateLimitMiddleware
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.routers import auth, changes, comments, documents, notifications, webhooks
from src.services.sync_service import seed_if_empty

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the application for the duration of its lifetime.
    """
    # Startup: seed docs from GitHub if the database is empty
    settings = get_settings()
    if settings.environment != "test":
        # Use GITHUB_SEED_TOKEN if available, otherwise try unauthenticated.
        # A token is required for private repos.
        seed_token = settings.github_seed_token or ""
        github = GitHubClient(
            token=seed_token,
            repo_owner=settings.github_repo_owner,
            repo_name=settings.github_repo_name,
        )
        try:
            async with async_session_factory() as db:
                await seed_if_empty(db, github)
        except Exception:
            logger.warning("Startup seed failed — docs will be empty until webhook fires")
        finally:
            await github.close()

    yield
    # Shutdown: any cleanup goes here


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A fully configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(
        title="dev-workflows-app",
        description="API for the dev-workflows engineering handbook",
        version="0.1.0",
        lifespan=lifespan,
    )

    # --- Middleware (applied in reverse order — last added runs first) ---

    # CORS: restrict to known origins, methods, and headers
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Security headers on every response
    application.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting per IP
    application.add_middleware(RateLimitMiddleware)

    # --- Global exception handler ---
    # Catches unhandled exceptions and returns a generic error message
    # to prevent leaking internal details (stack traces, DB errors, etc.)

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a generic error response for unhandled exceptions.

        Logs the full exception server-side for debugging but returns
        only a safe message to the client.

        Args:
            request: The request that caused the exception.
            exc: The unhandled exception.

        Returns:
            A 500 JSON response with a generic error message.
        """
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred."},
        )

    # --- Routers ---
    application.include_router(auth.router)
    application.include_router(documents.router)
    application.include_router(comments.router)
    application.include_router(changes.router)
    application.include_router(notifications.router)
    application.include_router(webhooks.router)

    @application.get("/api/health")
    async def health_check() -> dict[str, str]:
        """Return a simple health check response.

        Returns:
            A dict with status "ok".
        """
        return {"status": "ok"}

    return application


app = create_app()
