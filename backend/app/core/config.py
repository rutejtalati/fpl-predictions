from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    apifootball_api_key: str | None = None
    backend_cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
