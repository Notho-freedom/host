"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json


class TestAPIRoutes:
    """Test API route functionality."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "TTS Service"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint."""
        with patch('src.services.tts_service.tts_service.get_all_voices') as mock_voices:
            mock_voices.return_value = [{"name": "test-voice"}]
            
            response = await async_client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_status_endpoint(self, async_client: AsyncClient):
        """Test status endpoint."""
        with patch('src.services.tts_service.tts_service.get_service_stats') as mock_stats:
            mock_stats.return_value = {"voice_cache": {}, "audio_cache": {}}
            
            response = await async_client.get("/api/status")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "OK"
            assert data["message"] == "TTS service is operational"

    @pytest.mark.asyncio
    async def test_voices_endpoint(self, async_client: AsyncClient):
        """Test voices listing endpoint."""
        mock_voices = [
            {"Name": "fr-FR-DeniseNeural", "Gender": "Female"},
            {"Name": "en-US-AriaNeural", "Gender": "Female"}
        ]
        
        with patch('src.services.tts_service.tts_service.get_all_voices') as mock:
            mock.return_value = mock_voices
            
            response = await async_client.get("/api/voices")
            assert response.status_code == 200
            data = response.json()
            assert "voices" in data
            assert data["count"] == 2

    @pytest.mark.asyncio
    async def test_check_voice_valid(self, async_client: AsyncClient):
        """Test voice availability check with valid voice."""
        with patch('src.services.tts_service.tts_service.check_voice_availability') as mock:
            mock.return_value = True
            
            response = await async_client.get("/api/check-voice/fr-FR-DeniseNeural")
            assert response.status_code == 200
            data = response.json()
            assert data["voice"] == "fr-FR-DeniseNeural"
            assert data["available"] is True

    @pytest.mark.asyncio
    async def test_check_voice_invalid_format(self, async_client: AsyncClient):
        """Test voice availability check with invalid format."""
        response = await async_client.get("/api/check-voice/invalid-voice-name")
        assert response.status_code == 400
        data = response.json()
        assert "Invalid voice name format" in data["detail"]

    @pytest.mark.asyncio
    async def test_voices_by_language(self, async_client: AsyncClient):
        """Test voices by language endpoint."""
        mock_voices_data = {
            "male_voices": [],
            "female_voices": [
                {
                    "name": "fr-FR-DeniseNeural",
                    "display_name": "Denise",
                    "locale": "fr-FR",
                    "gender": "Female"
                }
            ]
        }
        
        with patch('src.services.tts_service.tts_service.get_voices_by_language') as mock:
            mock.return_value = mock_voices_data
            
            response = await async_client.get("/api/voices-by-language/fr")
            assert response.status_code == 200
            data = response.json()
            assert "male_voices" in data
            assert "female_voices" in data
            assert len(data["female_voices"]) == 1

    @pytest.mark.asyncio
    async def test_voices_by_text(self, async_client: AsyncClient):
        """Test voices by text analysis."""
        request_data = {"text": "Bonjour, comment allez-vous?"}
        mock_voices_data = {
            "male_voices": [],
            "female_voices": [
                {
                    "name": "fr-FR-DeniseNeural",
                    "display_name": "Denise",
                    "locale": "fr-FR",
                    "gender": "Female"
                }
            ]
        }
        
        with patch('src.services.tts_service.tts_service.detect_language') as mock_detect:
            with patch('src.services.tts_service.tts_service.get_voices_by_language') as mock_voices:
                mock_detect.return_value = "fr"
                mock_voices.return_value = mock_voices_data
                
                response = await async_client.post("/api/voices-by-text", json=request_data)
                assert response.status_code == 200
                data = response.json()
                assert "male_voices" in data
                assert "female_voices" in data

    @pytest.mark.asyncio
    async def test_tts_generation(self, async_client: AsyncClient):
        """Test TTS audio generation."""
        request_data = {
            "text": "Hello world",
            "voice": "en-US-AriaNeural"
        }
        
        mock_audio_data = b"fake_audio_content"
        
        with patch('src.services.tts_service.tts_service.generate_audio') as mock:
            from io import BytesIO
            mock_audio_buffer = BytesIO(mock_audio_data)
            mock.return_value = mock_audio_buffer
            
            response = await async_client.post("/api/tts", json=request_data)
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"
            assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_tts_validation_error(self, async_client: AsyncClient):
        """Test TTS with validation errors."""
        # Test with empty text
        request_data = {"text": "", "voice": "fr-FR-DeniseNeural"}
        
        response = await async_client.post("/api/tts", json=request_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_tts_forbidden_characters(self, async_client: AsyncClient):
        """Test TTS with forbidden characters."""
        request_data = {
            "text": "Hello <script>alert('xss')</script>",
            "voice": "en-US-AriaNeural"
        }
        
        response = await async_client.post("/api/tts", json=request_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_stats_endpoint(self, async_client: AsyncClient):
        """Test service statistics endpoint."""
        mock_stats = {
            "voice_cache": {"size": 10, "hits": 100},
            "audio_cache": {"size": 5, "hits": 50},
            "total_voices": 200
        }
        
        with patch('src.services.tts_service.tts_service.get_service_stats') as mock:
            mock.return_value = mock_stats
            
            response = await async_client.get("/api/stats")
            assert response.status_code == 200
            data = response.json()
            assert "voice_cache" in data
            assert "audio_cache" in data
            assert data["total_voices"] == 200