import os
import logging
import json
from typing import List, Union, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

# Load .env from the correct location if it exists
env_path = Path("forge-service") / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    app_name: str = "Forge API"
    version: str = "v2.0"
    environment: str = Field(default="production", env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    port: int = Field(default=8000, env="PORT")
    
    # ✅ Use Any type and let validator handle conversion
    cors_origins: Any = Field(default="*", env="CORS_ORIGINS")
    
    enable_legacy: bool = Field(default=True, env="FORGE_ENABLE_LEGACY")

    # Chroma DB Configuration
    chroma_server_host: str = Field(default="0.0.0.0", env="CHROMA_SERVER_HOST")
    chroma_server_http_port: int = Field(default=8000, env="CHROMA_SERVER_HTTP_PORT")
    chroma_server_grpc_port: int = Field(default=50051, env="CHROMA_SERVER_GRPC_PORT")
    chroma_server_cors_allow_origins: Any = Field(
        default="http://localhost:3000",
        env="CHROMA_SERVER_CORS_ALLOW_ORIGINS"
    )
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")

    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string to list"""
        if v is None:
            return ["*"]
        
        if isinstance(v, list):
            return v
            
        if isinstance(v, str):
            v = v.strip()
            # Handle JSON array format
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in CORS_ORIGINS: {v}")
                    return ["*"]
            # Handle wildcard or comma-separated
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return ["*"]

    @field_validator("chroma_server_cors_allow_origins", mode="before")
    def parse_chroma_cors_origins(cls, v):
        """Parse CHROMA_SERVER_CORS_ALLOW_ORIGINS from string to list"""
        if v is None:
            return ["http://localhost:3000"]
        
        if isinstance(v, list):
            return v
            
        if isinstance(v, str):
            v = v.strip()
            # Handle JSON array format
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in CHROMA_SERVER_CORS_ALLOW_ORIGINS: {v}")
                    return ["http://localhost:3000"]
            # Handle wildcard or comma-separated
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return ["http://localhost:3000"]

    # ... keep the port validators the same ...

# Create settings instance
try:
    settings = Settings()
    logger.info(f"✅ Successfully loaded config for {settings.app_name} v{settings.version}")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🌐 CORS origins: {settings.cors_origins}")
    logger.info(f"🔧 Chroma CORS: {settings.chroma_server_cors_allow_origins}")
except Exception as e:
    logger.error(f"❌ Failed to load settings: {e}")
    import sys
    sys.exit(1)
