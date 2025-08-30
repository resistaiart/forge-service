# forge/config.py — Centralized settings management
import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load .env if available
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Forge API"
    port: int = Field(default=8000, env="PORT")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
