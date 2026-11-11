
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Adaptive Web Crawler"
    app_version: str = "0.1.0"
    app_env: str = "development"

    # PostgreSQL database connections
    database_url: str
    direct_url: str

    max_concurrency: int = 3
    request_timeout: int = 30
    max_retries: int = 3

    default_fetcher: str = "fetcher"
    robots_txt_obey: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
