"""FastAPI application factory and startup configuration.

This is the entry point for the backend API. Uvicorn loads this module
to serve the application.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.routers import auth, changes, comments, documents, notifications, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the application for the duration of its lifetime.
    """
    # Startup: any initialization goes here
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

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
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
