"""Application settings, read from environment variables or a .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env")

    database_url: str = f"sqlite:///{BACKEND_DIR / 'sprintboard.db'}"
    secret_key: str = "dev-only-secret-key-change-me-in-production"
    access_token_expire_minutes: int = 60 * 8
    log_level: str = "INFO"
    # Optional: an admin account recreated on every start (e.g. after Render wipes the database).
    admin_username: str | None = None
    admin_password: str | None = None
    # Load the demo data (10+ records per table) on startup when there are no projects yet.
    load_demo_data: bool = True


settings = Settings()
