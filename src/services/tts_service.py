"""Text-to-Speech service with caching and error handling."""

import asyncio
import hashlib
from io import BytesIO
from typing import List, Optional, Dict, Any
import logging

from src.models.schemas import VoiceInfo, Gender
from src.utils.cache import cache_async, cache_manager
from src.core.config import settings

# Import with fallback for missing dependencies
try:
    import edge_tts
except ImportError:
    print("Warning: edge-tts not installed. TTS functionality will be limited.")
    edge_tts = None

try:
    from langdetect import detect, DetectorFactory
    # Set seed for consistent language detection
    DetectorFactory.seed = 0
except ImportError:
    print("Warning: langdetect not installed. Language detection will use fallback.")
    detect = None
    DetectorFactory = None

# Set seed for consistent language detection
if DetectorFactory is not None:
    DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class TTSService:
    """Enhanced Text-to-Speech service."""
    
    def __init__(self):
        self.voice_cache = cache_manager.get_cache(
            "voices", 
            ttl=settings.cache_ttl_voices,
            max_size=100
        )
        self.audio_cache = cache_manager.get_cache(
            "audio",
            ttl=settings.cache_ttl_audio,
            max_size=50
        )
    
    @cache_async(ttl=3600, cache_name="voices")
    async def get_all_voices(self) -> List[Dict[str, Any]]:
        """Get all available voices with caching."""
        if edge_tts is None:
            logger.error("edge-tts not available")
            raise RuntimeError("edge-tts dependency not installed")
            
        try:
            voices = await edge_tts.list_voices()
            logger.info(f"Retrieved {len(voices)} voices from edge-tts")
            return voices
        except Exception as e:
            logger.error(f"Failed to retrieve voices: {e}")
            raise RuntimeError("Unable to fetch available voices") from e
    
    async def get_voices_by_language(self, language_code: str) -> Dict[str, List[VoiceInfo]]:
        """Get voices filtered by language and gender."""
        try:
            all_voices = await self.get_all_voices()
            language_prefix = language_code.lower()
            
            male_voices = []
            female_voices = []
            
            for voice in all_voices:
                if not voice.get('Locale', '').lower().startswith(language_prefix):
                    continue
                
                voice_info = VoiceInfo(
                    name=voice.get('ShortName', voice.get('Name', '')),
                    display_name=voice.get('FriendlyName', voice.get('DisplayName', '')),
                    locale=voice.get('Locale', ''),
                    gender=Gender(voice.get('Gender', 'Male')),
                    sample_rate_hertz=voice.get('SampleRateHertz'),
                    voice_type=voice.get('VoiceType')
                )
                
                if voice_info.gender == Gender.MALE:
                    male_voices.append(voice_info)
                else:
                    female_voices.append(voice_info)
            
            return {
                "male_voices": male_voices,
                "female_voices": female_voices
            }
            
        except Exception as e:
            logger.error(f"Failed to filter voices by language {language_code}: {e}")
            raise RuntimeError(f"Unable to get voices for language {language_code}") from e
    
    async def detect_language(self, text: str) -> str:
        """Detect language from text with error handling."""
        if detect is None:
            logger.warning("langdetect not available, using default language")
            return "fr"
            
        try:
            # Clean text for better detection
            clean_text = text.strip()[:1000]  # Limit text for detection
            
            if len(clean_text) < 3:
                return "fr"  # Default fallback
            
            detected_lang = detect(clean_text)
            logger.info(f"Detected language: {detected_lang} for text: '{clean_text[:50]}...'")
            return detected_lang
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Using default 'fr'")
            return "fr"  # Fallback to French
    
    async def check_voice_availability(self, voice_name: str) -> bool:
        """Check if a specific voice is available."""
        try:
            all_voices = await self.get_all_voices()
            available_names = {
                voice.get('ShortName', voice.get('Name', ''))
                for voice in all_voices
            }
            return voice_name in available_names
            
        except Exception as e:
            logger.error(f"Failed to check voice availability for {voice_name}: {e}")
            return False
    
    async def generate_audio(self, text: str, voice: Optional[str] = None) -> BytesIO:
        """Generate audio from text with caching."""
        if edge_tts is None:
            logger.error("edge-tts not available")
            raise RuntimeError("edge-tts dependency not installed")
            
        # Create cache key
        voice_to_use = voice or settings.default_voice
        cache_key = hashlib.md5(f"{text}:{voice_to_use}".encode()).hexdigest()
        
        # Try to get from cache
        cached_audio = await self.audio_cache.get(cache_key)
        if cached_audio:
            logger.info(f"Audio cache hit for key: {cache_key}")
            return BytesIO(cached_audio)
        
        try:
            # Validate voice if provided
            if voice and not await self.check_voice_availability(voice):
                logger.warning(f"Voice {voice} not available, using default")
                voice_to_use = settings.default_voice
            
            # Generate audio
            logger.info(f"Generating audio for text: '{text[:50]}...' with voice: {voice_to_use}")
            communicate = edge_tts.Communicate(text, voice_to_use)
            audio_buffer = BytesIO()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            
            audio_buffer.seek(0)
            audio_data = audio_buffer.getvalue()
            
            # Cache the result
            await self.audio_cache.set(cache_key, audio_data)
            
            # Return new BytesIO with the data
            return BytesIO(audio_data)
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise RuntimeError("Audio generation failed") from e
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get TTS service statistics."""
        try:
            voice_stats = await self.voice_cache.get_stats()
            audio_stats = await self.audio_cache.get_stats()
            
            return {
                "voice_cache": voice_stats,
                "audio_cache": audio_stats,
                "total_voices": len(await self.get_all_voices())
            }
        except Exception as e:
            logger.error(f"Failed to get service stats: {e}")
            return {"error": "Unable to retrieve stats"}


# Global TTS service instance
tts_service = TTSService()