from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Model Configuration
    default_model: str = "anthropic/claude-3-5-sonnet-20241022"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # Memory Configuration
    memory_provider: str = "mem0"
    chroma_persist_directory: Path = Path("./data/vector_db")
    memory_decay_days: int = 90

    # Google APIs
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8501"

    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    data_dir: Path = Path("./data")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
