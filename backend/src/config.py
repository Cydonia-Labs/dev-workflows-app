"""Application configuration loaded from environment variables.

Uses Pydantic BaseSettings to validate and type-check all configuration
at startup. The app fails fast if any required variable is missing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection string.
        secret_key: Key used to sign JWT session tokens.
        github_client_id: OAuth App client ID.
        github_client_secret: OAuth App client secret.
        github_webhook_secret: HMAC secret for webhook signature validation.
        github_repo_owner: GitHub username or org that owns the handbook repo.
        github_repo_name: Name of the handbook repo.
        vapid_private_key: VAPID private key for Web Push signing.
        vapid_public_key: VAPID public key shared with browsers.
        vapid_claim_email: Contact email included in VAPID claims.
        cors_origins: Comma-separated allowed CORS origins.
        environment: Runtime environment (development, production, test).
        log_level: Logging level.
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    secret_key: str
    github_client_id: str
    github_client_secret: str
    github_webhook_secret: str
    github_repo_owner: str = "stevemcgregory"
    github_repo_name: str = "dev-workflows"
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claim_email: str = ""
    cors_origins: str = "http://localhost:5173"
    environment: str = "development"
    log_level: str = "debug"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list.

        Returns:
            List of allowed origin URLs.
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]


def get_settings() -> Settings:
    """Create and return application settings.

    Returns:
        Validated Settings instance loaded from environment.
    """
    return Settings()
