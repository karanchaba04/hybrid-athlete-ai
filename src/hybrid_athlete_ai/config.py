from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./hybrid_athlete.db"
    app_name: str = "Hybrid Athlete AI"
    debug: bool = False


settings = Settings()
