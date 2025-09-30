"""Tests for TTS service functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO

from src.services.tts_service import tts_service
from src.models.schemas import Gender


class TestTTSService:
    """Test TTS service functionality."""

    @pytest.mark.asyncio
    async def test_get_all_voices_cached(self):
        """Test voice retrieval with caching."""
        mock_voices = [
            {"Name": "fr-FR-DeniseNeural", "Gender": "Female", "Locale": "fr-FR"},
            {"Name": "en-US-AriaNeural", "Gender": "Female", "Locale": "en-US"}
        ]
        
        # Clear cache first
        await tts_service.voice_cache.clear()
        
        with patch('edge_tts.list_voices') as mock_edge:
            mock_edge.return_value = mock_voices
            
            # First call should fetch from edge-tts
            voices1 = await tts_service.get_all_voices()
            assert len(voices1) == 2
            
            # Second call should use cache (edge-tts should not be called again)
            voices2 = await tts_service.get_all_voices()
            assert voices1 == voices2
            
            # Verify edge-tts was called only once due to caching
            mock_edge.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_voices_by_language_french(self):
        """Test filtering voices by French language."""
        mock_voices = [
            {
                "ShortName": "fr-FR-DeniseNeural",
                "FriendlyName": "Denise",
                "Gender": "Female",
                "Locale": "fr-FR"
            },
            {
                "ShortName": "fr-CA-SylvieNeural", 
                "FriendlyName": "Sylvie",
                "Gender": "Female",
                "Locale": "fr-CA"
            },
            {
                "ShortName": "en-US-AriaNeural",
                "FriendlyName": "Aria", 
                "Gender": "Female",
                "Locale": "en-US"
            }
        ]
        
        with patch.object(tts_service, 'get_all_voices') as mock_voices_method:
            mock_voices_method.return_value = mock_voices
            
            result = await tts_service.get_voices_by_language("fr")
            
            assert len(result["male_voices"]) == 0
            assert len(result["female_voices"]) == 2
            
            # Check that both French voices are included
            french_voice_names = [v.name for v in result["female_voices"]]
            assert "fr-FR-DeniseNeural" in french_voice_names
            assert "fr-CA-SylvieNeural" in french_voice_names

    @pytest.mark.asyncio
    async def test_detect_language_french(self):
        """Test language detection for French text."""
        french_text = "Bonjour, comment allez-vous aujourd'hui?"
        
        with patch('src.services.tts_service.detect') as mock_detect:
            mock_detect.return_value = "fr"
            
            result = await tts_service.detect_language(french_text)
            assert result == "fr"
            mock_detect.assert_called_once_with(french_text)

    @pytest.mark.asyncio
    async def test_detect_language_fallback(self):
        """Test language detection fallback on error."""
        with patch('src.services.tts_service.detect') as mock_detect:
            mock_detect.side_effect = Exception("Detection failed")
            
            result = await tts_service.detect_language("Some text")
            assert result == "fr"  # Should fallback to French

    @pytest.mark.asyncio
    async def test_detect_language_short_text(self):
        """Test language detection with very short text."""
        short_text = "Hi"
        
        result = await tts_service.detect_language(short_text)
        assert result == "fr"  # Should fallback for short text

    @pytest.mark.asyncio
    async def test_check_voice_availability_exists(self):
        """Test voice availability check for existing voice."""
        mock_voices = [
            {"ShortName": "fr-FR-DeniseNeural", "Name": "Microsoft Server Speech Text to Speech Voice (fr-FR, DeniseNeural)"}
        ]
        
        with patch.object(tts_service, 'get_all_voices') as mock:
            mock.return_value = mock_voices
            
            result = await tts_service.check_voice_availability("fr-FR-DeniseNeural")
            assert result is True

    @pytest.mark.asyncio
    async def test_check_voice_availability_not_exists(self):
        """Test voice availability check for non-existing voice."""
        mock_voices = [
            {"ShortName": "fr-FR-DeniseNeural"}
        ]
        
        with patch.object(tts_service, 'get_all_voices') as mock:
            mock.return_value = mock_voices
            
            result = await tts_service.check_voice_availability("non-existent-voice")
            assert result is False

    @pytest.mark.asyncio
    async def test_generate_audio_success(self):
        """Test successful audio generation."""
        text = "Hello world"
        voice = "en-US-AriaNeural"
        mock_audio_data = b"fake_audio_content"
        
        # Mock the edge_tts.Communicate class
        async def mock_stream():
            yield {"type": "audio", "data": mock_audio_data}
        
        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream()
        
        with patch('edge_tts.Communicate') as mock_edge_communicate:
            with patch.object(tts_service, 'check_voice_availability') as mock_check:
                mock_edge_communicate.return_value = mock_communicate
                mock_check.return_value = True
                
                result = await tts_service.generate_audio(text, voice)
                
                assert isinstance(result, BytesIO)
                assert result.getvalue() == mock_audio_data

    @pytest.mark.asyncio
    async def test_generate_audio_invalid_voice(self):
        """Test audio generation with invalid voice falls back to default."""
        text = "Hello world"
        invalid_voice = "invalid-voice"
        mock_audio_data = b"fake_audio_content"
        
        async def mock_stream():
            yield {"type": "audio", "data": mock_audio_data}
        
        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream()
        
        with patch('edge_tts.Communicate') as mock_edge_communicate:
            with patch.object(tts_service, 'check_voice_availability') as mock_check:
                mock_edge_communicate.return_value = mock_communicate
                mock_check.return_value = False  # Invalid voice
                
                result = await tts_service.generate_audio(text, invalid_voice)
                
                # Should use default voice instead
                mock_edge_communicate.assert_called_with(text, "fr-FR-DeniseNeural")
                assert isinstance(result, BytesIO)

    @pytest.mark.asyncio
    async def test_generate_audio_caching(self):
        """Test audio generation caching."""
        text = "Hello world"
        voice = "en-US-AriaNeural"
        mock_audio_data = b"fake_audio_content"
        
        # Clear cache first
        await tts_service.audio_cache.clear()
        
        # First call - should generate audio
        async def mock_stream2():
            yield {"type": "audio", "data": mock_audio_data}
            
        mock_communicate = MagicMock()
        mock_communicate.stream.return_value = mock_stream2()
        
        with patch('edge_tts.Communicate') as mock_edge_communicate:
            with patch.object(tts_service, 'check_voice_availability') as mock_check:
                mock_edge_communicate.return_value = mock_communicate
                mock_check.return_value = True
                
                # First call
                result1 = await tts_service.generate_audio(text, voice)
                assert result1.getvalue() == mock_audio_data
                
                # Second call should use cache
                result2 = await tts_service.generate_audio(text, voice)
                assert result2.getvalue() == mock_audio_data
                
                # Edge TTS should only be called once
                mock_edge_communicate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_stats(self):
        """Test service statistics retrieval."""
        with patch.object(tts_service, 'get_all_voices') as mock_voices:
            mock_voices.return_value = [{"name": "voice1"}, {"name": "voice2"}]
            
            stats = await tts_service.get_service_stats()
            
            assert "voice_cache" in stats
            assert "audio_cache" in stats
            assert stats["total_voices"] == 2