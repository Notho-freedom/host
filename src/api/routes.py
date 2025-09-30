"""API routes for TTS service."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import logging

from src.models.schemas import (
    TTSRequest, VoicesByTextRequest, VoicesResponse,
    VoiceAvailabilityResponse, StatusResponse, ErrorResponse
)
from src.services.tts_service import tts_service
from src.utils.security import SecurityValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["tts"])


async def validate_tts_request(request: TTSRequest) -> TTSRequest:
    """Validate and sanitize TTS request."""
    # Sanitize text
    request.text = SecurityValidator.sanitize_text(request.text)
    
    # Validate voice name if provided
    if request.voice and not SecurityValidator.validate_voice_name(request.voice):
        logger.warning(f"Invalid voice name format: {request.voice}")
        request.voice = None  # Will use default
    
    return request


@router.post("/tts", response_model=None)
async def generate_tts(
    request: TTSRequest = Depends(validate_tts_request)
):
    """Generate Text-to-Speech audio."""
    try:
        logger.info(f"TTS request: '{request.text[:30]}...' with voice '{request.voice}'")
        
        audio_buffer = await tts_service.generate_audio(
            text=request.text,
            voice=request.voice
        )
        
        return StreamingResponse(
            content=iter([audio_buffer.getvalue()]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=tts_audio.mp3",
                "Cache-Control": "public, max-age=300"  # Cache for 5 minutes
            }
        )
        
    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Audio generation failed"
        )


@router.get("/voices", response_model=Dict[str, Any])
async def list_voices():
    """Get all available voices."""
    try:
        voices = await tts_service.get_all_voices()
        return {"voices": voices, "count": len(voices)}
        
    except Exception as e:
        logger.error(f"Error fetching voices: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve voices"
        )


@router.get("/check-voice/{voice_name}", response_model=VoiceAvailabilityResponse)
async def check_voice(voice_name: str):
    """Check if a specific voice is available."""
    try:
        # Validate voice name format
        if not SecurityValidator.validate_voice_name(voice_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid voice name format"
            )
        
        available = await tts_service.check_voice_availability(voice_name)
        
        return VoiceAvailabilityResponse(
            voice=voice_name,
            available=available
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking voice {voice_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check voice availability"
        )


@router.post("/voices-by-text", response_model=VoicesResponse)
async def get_voices_by_text(request: VoicesByTextRequest):
    """Get voices based on detected language from text."""
    try:
        # Sanitize input
        clean_text = SecurityValidator.sanitize_text(request.text)
        
        # Detect language
        language_code = await tts_service.detect_language(clean_text)
        
        # Get voices for the detected language
        voices_data = await tts_service.get_voices_by_language(language_code)
        
        return VoicesResponse(**voices_data)
        
    except Exception as e:
        logger.error(f"Error getting voices for text: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze text and retrieve voices"
        )


@router.get("/voices-by-language/{language_code}", response_model=VoicesResponse)
async def get_voices_by_language(language_code: str):
    """Get voices filtered by language and gender."""
    try:
        # Validate language code format
        if not language_code or len(language_code) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid language code"
            )
        
        voices_data = await tts_service.get_voices_by_language(language_code)
        
        return VoicesResponse(**voices_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voices for language {language_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve voices for language {language_code}"
        )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get service status and health information."""
    try:
        from src.core.config import settings
        
        # Get service statistics
        stats = await tts_service.get_service_stats()
        
        return StatusResponse(
            status="OK",
            message="TTS service is operational",
            version=settings.version
        )
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve service status"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_service_stats():
    """Get detailed service statistics (admin endpoint)."""
    try:
        stats = await tts_service.get_service_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve service statistics"
        )