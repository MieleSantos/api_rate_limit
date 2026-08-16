"""
Configuration module.

Loads environment variables and sets up application configurations.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings derived from environment variables.
    
    Attributes:
        rate_limit_requests: Maximum number of requests allowed per window.
        rate_limit_window_seconds: Duration of the rate limit window in seconds.
    """
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
