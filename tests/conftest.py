"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    from fastapi import FastAPI
    from httpx import ASGITransport
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def sample_tts_request():
    """Sample TTS request data."""
    return {
        "text": "Bonjour, ceci est un test de synthèse vocale.",
        "voice": "fr-FR-DeniseNeural"
    }


@pytest.fixture
def sample_text_request():
    """Sample text for language detection."""
    return {
        "text": "Hello, this is a test for language detection."
    }