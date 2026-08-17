from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./hybrid_athlete.db"
    app_name: str = "Hybrid Athlete AI"
    debug: bool = False

    anthropic_api_key: str | None = None
    coach_model: str = "claude-sonnet-5"
    coach_temperature: float = 0.3


settings = Settings()
