"""
Build 88 Configuration Settings.
Provides environment-backed configurations for Weaviate vector database and recipe semantic search.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory resolution
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()


class Settings:
    """
    Application and Weaviate runtime configuration.
    """

    # Server Settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Weaviate Vector Database Settings
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "mock-weaviate-api-key")
    WEAVIATE_CLASS_NAME: str = os.getenv("WEAVIATE_CLASS_NAME", "Recipe")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "128"))
    EMBEDDING_DIMENSION: int = VECTOR_DIMENSION
    USE_EMBEDDED_ENGINE: bool = os.getenv("USE_EMBEDDED_ENGINE", "true").lower() in ("true", "1", "yes")

    # Search & Ranking Defaults
    DEFAULT_CERTAINTY_THRESHOLD: float = float(os.getenv("DEFAULT_CERTAINTY_THRESHOLD", "0.50"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "5"))


settings = Settings()
