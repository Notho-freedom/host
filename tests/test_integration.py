"""Integration tests for the complete application."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_tts_workflow(self, async_client: AsyncClient):
        """Test complete TTS workflow from text analysis to audio generation."""
        
        # Mock data
        mock_voices = [
            {
                "ShortName": "fr-FR-DeniseNeural",
                "FriendlyName": "Denise (France)",
                "Gender": "Female",
                "Locale": "fr-FR",
                "SampleRateHertz": "24000",
                "VoiceType": "Neural"
            },
            {
                "ShortName": "fr-FR-HenriNeural", 
                "FriendlyName": "Henri (France)",
                "Gender": "Male",
                "Locale": "fr-FR",
                "SampleRateHertz": "24000",
                "VoiceType": "Neural"
            }
        ]
        
        french_text = "Bonjour, ceci est un test complet du système TTS."
        
        with patch('edge_tts.list_voices') as mock_list_voices:
            with patch('langdetect.detect') as mock_detect:
                with patch('edge_tts.Communicate') as mock_communicate:
                    
                    # Setup mocks
                    mock_list_voices.return_value = mock_voices
                    mock_detect.return_value = "fr"
                    
                    async def mock_stream():
                        yield {"type": "audio", "data": b"fake_french_audio"}
                    
                    mock_comm_instance = mock_communicate.return_value
                    mock_comm_instance.stream.return_value = mock_stream()
                    
                    # Step 1: Check service status
                    status_response = await async_client.get("/api/status")
                    assert status_response.status_code == 200
                    status_data = status_response.json()
                    assert status_data["status"] == "OK"
                    
                    # Step 2: Get voices by text (language detection)
                    text_request = {"text": french_text}
                    voices_response = await async_client.post("/api/voices-by-text", json=text_request)
                    assert voices_response.status_code == 200
                    voices_data = voices_response.json()
                    
                    # Verify we got French voices
                    assert len(voices_data["female_voices"]) == 1
                    assert len(voices_data["male_voices"]) == 1
                    assert voices_data["female_voices"][0]["name"] == "fr-FR-DeniseNeural"
                    
                    # Step 3: Check voice availability
                    voice_check_response = await async_client.get("/api/check-voice/fr-FR-DeniseNeural")
                    assert voice_check_response.status_code == 200
                    voice_check_data = voice_check_response.json()
                    assert voice_check_data["available"] is True
                    
                    # Step 4: Generate TTS audio
                    tts_request = {
                        "text": french_text,
                        "voice": "fr-FR-DeniseNeural"
                    }
                    tts_response = await async_client.post("/api/tts", json=tts_request)
                    assert tts_response.status_code == 200
                    assert tts_response.headers["content-type"] == "audio/mpeg"
                    assert len(tts_response.content) > 0
                    
                    # Verify the workflow called appropriate services
                    mock_detect.assert_called_with(french_text)
                    mock_communicate.assert_called_with(french_text, "fr-FR-DeniseNeural")

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, async_client: AsyncClient):
        """Test error handling throughout the application."""
        
        # Test with service unavailable
        with patch('edge_tts.list_voices') as mock_list_voices:
            mock_list_voices.side_effect = Exception("Service unavailable")
            
            # Should handle gracefully
            response = await async_client.get("/api/voices")
            assert response.status_code == 500
            error_data = response.json()
            assert "Failed to retrieve voices" in error_data["detail"]

    @pytest.mark.asyncio
    async def test_rate_limiting_workflow(self, async_client: AsyncClient):
        """Test rate limiting functionality."""
        
        # Mock successful service
        with patch('edge_tts.list_voices') as mock_voices:
            mock_voices.return_value = []
            
            # Make multiple rapid requests
            responses = []
            for _ in range(5):  # Well within normal rate limit
                response = await async_client.get("/api/status")
                responses.append(response)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_caching_workflow(self, async_client: AsyncClient):
        """Test caching behavior across requests."""
        
        mock_voices = [{"ShortName": "test-voice", "Gender": "Female", "Locale": "en-US"}]
        
        with patch('edge_tts.list_voices') as mock_list_voices:
            mock_list_voices.return_value = mock_voices
            
            # First request should hit the service
            response1 = await async_client.get("/api/voices")
            assert response1.status_code == 200
            
            # Second request should use cache (same result, but service not called again)
            response2 = await async_client.get("/api/voices")
            assert response2.status_code == 200
            
            # Verify data consistency
            assert response1.json() == response2.json()

    @pytest.mark.asyncio
    async def test_validation_workflow(self, async_client: AsyncClient):
        """Test input validation throughout the API."""
        
        # Test text validation
        invalid_requests = [
            {"text": ""},  # Empty text
            {"text": "Hello <script>"},  # Forbidden characters
            {"text": "x" * 15000},  # Too long text
        ]
        
        for invalid_request in invalid_requests:
            response = await async_client.post("/api/tts", json=invalid_request)
            assert response.status_code == 422  # Validation error
        
        # Test voice name validation
        response = await async_client.get("/api/check-voice/invalid-format")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_health_monitoring_workflow(self, async_client: AsyncClient):
        """Test health monitoring and diagnostics."""
        
        with patch('edge_tts.list_voices') as mock_voices:
            mock_voices.return_value = [{"name": "test"}]
            
            # Health check should pass
            health_response = await async_client.get("/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            
            # Stats should be available
            stats_response = await async_client.get("/api/stats")
            assert stats_response.status_code == 200
            stats_data = stats_response.json()
            assert "voice_cache" in stats_data
            assert "audio_cache" in stats_data