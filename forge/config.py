import os
import logging
import json
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, validator

# Load .env from the correct location
env_path = Path("forge-service") / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    app_name: str = "Forge API"
    version: str = "v2.0"
    environment: str = Field(default="production", env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    port: int = Field(default=8000, env="PORT")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    enable_legacy: bool = Field(default=True, env="FORGE_ENABLE_LEGACY")

    # Chroma DB Configuration
    chroma_server_host: str = Field(default="0.0.0.0", env="CHROMA_SERVER_HOST")
    chroma_server_http_port: int = Field(default=8000, env="CHROMA_SERVER_HTTP_PORT")
    chroma_server_grpc_port: int = Field(default=50051, env="CHROMA_SERVER_GRPC_PORT")
    chroma_server_cors_allow_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        env="CHROMA_SERVER_CORS_ALLOW_ORIGINS"
    )
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")

    class Config:
        env_file_encoding = "utf-8"

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle JSON string format
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON format for CORS_ORIGINS: {v}")
                    return ["*"]
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("chroma_server_cors_allow_origins", pre=True)
    def parse_chroma_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle JSON string format
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON format for CORS origins: {v}")
                    return ["http://localhost:3000"]
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("PORT must be between 1 and 65535")
        return v

    @validator("chroma_server_http_port")
    def validate_chroma_http_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("CHROMA_SERVER_HTTP_PORT must be between 1 and 65535")
        return v

    @validator("chroma_server_grpc_port")
    def validate_chroma_grpc_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("CHROMA_SERVER_GRPC_PORT must be between 1 and 65535")
        return v

settings = Settings()

# Debug output to verify Chroma settings
logger.info(f"Loaded config for {settings.app_name} v{settings.version}")
logger.info(f"Chroma CORS origins: {settings.chroma_server_cors_allow_origins}")
logger.info(f"Chroma HTTP port: {settings.chroma_server_http_port}")
logger.info(f"Chroma gRPC port: {settings.chroma_server_grpc_port}")

# Used in `/version` endpoint
ENDPOINTS = {
    "legacy": [
        "/optimise", "/t2i", "/t2v",
        "/optimise/i2i", "/optimise/t2v", "/analyse"
    ],
    "sealed_workshop": ["/v2/optimise", "/v2/analyse"],
    "health": "/health",
    "version": "/version",
    "manifest": "/manifest"
}
