### Environment configuration using Pydantic Settings.

### Loads configuration from environment variables or .env file.


from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # WordPress Integration
    wordpress_base_url: str = "https://example.com"
    wordpress_api_key: str = ""
    
    # LLM API Keys
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    
    # Optional: Timeout settings
    api_timeout_seconds: int = 30
    
    @property
    def wordpress_headers(self) -> dict[str, str]:
        """Headers for WordPress API requests."""
        return {
            "X-API-Key": self.wordpress_api_key,
            "Content-Type": "application/json",
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience instance
settings = get_settings()