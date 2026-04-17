from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Klypup Research API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    data_backend: str = "sqlalchemy"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/klypup"
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    auth0_domain: str = ""
    auth0_audience: str = ""
    auth0_algorithms: str = "RS256"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    news_api_key: str = ""
    faiss_index_path: str = "data/faiss/index.bin"
    faiss_meta_path: str = "data/faiss/meta.json"

    cors_origins: str = "http://localhost:3000"
    external_request_timeout_seconds: int = 12
    external_request_retries: int = 2
    request_logging_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
