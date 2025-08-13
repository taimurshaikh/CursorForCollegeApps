from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path

# Absolute paths so configuration works regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
ABS_ENV_FILE = BACKEND_DIR / ".env"
ABS_DB_PATH = BACKEND_DIR / "app.db"


class Settings(BaseSettings):
    openai_api_key: str | None = None
    # Use absolute sqlite path by default
    database_url: str = f"sqlite:///{ABS_DB_PATH}"
    openai_model: str = "gpt-4o-mini"

    class Config:
        # Always load this absolute .env file if present
        env_file = str(ABS_ENV_FILE)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
