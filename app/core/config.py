from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
