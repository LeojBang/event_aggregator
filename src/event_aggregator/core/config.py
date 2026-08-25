from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_CONNECTION_STRING: str
    EVENTS_PROVIDER_URL: str
    EVENTS_PROVIDER_API_KEY: str
    OUTBOX_POLL_INTERVAL_SECONDS: int = 5
    CAPASHINO_URL: str
    CAPASHINO_API_KEY: str
    SENTRY_DSN: str | None = None

    @property
    def database_url(self):
        url = self.POSTGRES_CONNECTION_STRING
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
