"""Configuration management using Pydantic Settings."""

from typing import List
import os

# Import with compatibility for different pydantic versions
try:
    from pydantic_settings import BaseSettings
    from pydantic import validator
except ImportError:
    try:
        from pydantic import BaseSettings, validator
    except ImportError:
        print("Error: pydantic not available")
        raise


class Settings(BaseSettings):
    """Application settings."""
    
    # Server configuration
    app_name: str = "TTS Service"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "https://skyos.onrender.com",
        "https://skyos.genesis-company.net"
    ]
    max_text_length: int = 10000  # Maximum characters for TTS
    rate_limit_requests: int = 100  # Requests per minute per IP
    rate_limit_window: int = 60  # Time window in seconds
    
    # TTS Configuration
    default_voice: str = "fr-FR-DeniseNeural"
    max_audio_duration: int = 300  # Maximum audio duration in seconds
    
    # Cache configuration
    cache_ttl_voices: int = 3600  # Cache voices for 1 hour
    cache_ttl_audio: int = 300    # Cache audio for 5 minutes
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()