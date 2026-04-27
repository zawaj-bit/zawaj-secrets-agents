"""Configuration centralisée via variables d'environnement."""

import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")

    # Instagram
    instagram_access_token: str = Field(default="", alias="INSTAGRAM_ACCESS_TOKEN")
    instagram_account_id: str = Field(default="", alias="INSTAGRAM_ACCOUNT_ID")

    # Klaviyo
    klaviyo_api_key: str = Field(default="", alias="KLAVIYO_API_KEY")
    klaviyo_list_id: str = Field(default="", alias="KLAVIYO_LIST_ID")

    # Canva
    canva_access_token: str = Field(default="", alias="CANVA_ACCESS_TOKEN")
    canva_brand_kit_id: str = Field(default="", alias="CANVA_BRAND_KIT_ID")

    # Application
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Modèles Claude
    orchestrator_model: str = "claude-opus-4-7"
    agent_model: str = "claude-opus-4-7"

    class Config:
        populate_by_name = True
        env_file = ".env"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
