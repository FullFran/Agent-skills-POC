from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM Configuration
    LLM_API_KEY: str = "sk-..."
    LLM_MODEL: str = "gpt-4o"
    LLM_BASE_URL: str = "https://api.openai.com/v1"

    # Workspace
    WORKSPACE_DIR: str = "./workspace"
    SKILLS_DIR: str = "./workspace/skills"
    SOUL_FILE: str = "./workspace/soul.md"
    TOOLS_FILE: str = "./workspace/tools.md"

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
