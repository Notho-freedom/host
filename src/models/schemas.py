"""Pydantic models for request/response validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class Gender(str, Enum):
    """Voice gender enumeration."""
    MALE = "Male"
    FEMALE = "Female"


class TTSRequest(BaseModel):
    """Text-to-Speech request model."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to synthesize")
    voice: Optional[str] = Field(None, description="Voice to use for synthesis")
    
    @validator('text')
    def validate_text(cls, v):
        """Validate and sanitize text input."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        
        # Remove potentially dangerous characters
        forbidden_chars = ['<', '>', '&', '"', "'"]
        for char in forbidden_chars:
            if char in v:
                raise ValueError(f"Text contains forbidden character: {char}")
        
        return v.strip()


class VoicesByTextRequest(BaseModel):
    """Request model for getting voices by text analysis."""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to analyze for language detection")


class VoiceInfo(BaseModel):
    """Voice information model."""
    name: str = Field(..., description="Voice name")
    display_name: str = Field(..., description="Human-readable voice name") 
    locale: str = Field(..., description="Voice locale")
    gender: Gender = Field(..., description="Voice gender")
    sample_rate_hertz: Optional[str] = Field(None, description="Sample rate")
    voice_type: Optional[str] = Field(None, description="Voice type")


class VoicesResponse(BaseModel):
    """Response model for voices listing."""
    male_voices: List[VoiceInfo] = Field(default_factory=list)
    female_voices: List[VoiceInfo] = Field(default_factory=list)


class VoiceAvailabilityResponse(BaseModel):
    """Response model for voice availability check."""
    voice: str = Field(..., description="Voice name")
    available: bool = Field(..., description="Whether the voice is available")


class StatusResponse(BaseModel):
    """API status response model."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: Optional[str] = Field(None, description="API version")
    uptime: Optional[str] = Field(None, description="Service uptime")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    checks: Dict[str, Any] = Field(default_factory=dict, description="Individual health checks")
    timestamp: str = Field(..., description="Check timestamp")