#!/usr/bin/env python3
"""Modern test script for the TTS service."""

import asyncio
import aiohttp
import argparse
import json
import sys
from pathlib import Path
import time
import io

# Optional audio playback
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Warning: pygame not available. Audio playback disabled.")


class TTSTestClient:
    """Modern async test client for TTS service."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self):
        """Test service health."""
        print("🔍 Testing service health...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data['status']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_status(self):
        """Test status endpoint."""
        print("🔍 Testing status endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status OK: {data['message']}")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    return True
                else:
                    print(f"❌ Status check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
    
    async def test_voices(self):
        """Test voice listing."""
        print("🔍 Testing voice listing...")
        try:
            async with self.session.get(f"{self.base_url}/api/voices") as response:
                if response.status == 200:
                    data = await response.json()
                    count = data.get('count', 0)
                    print(f"✅ Retrieved {count} voices")
                    
                    # Show sample voices
                    voices = data.get('voices', [])
                    if voices:
                        print("   Sample voices:")
                        for voice in voices[:3]:
                            name = voice.get('ShortName', voice.get('Name', 'Unknown'))
                            locale = voice.get('Locale', 'Unknown')
                            gender = voice.get('Gender', 'Unknown')
                            print(f"   - {name} ({locale}, {gender})")
                    
                    return True
                else:
                    print(f"❌ Voice listing failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Voice listing error: {e}")
            return False
    
    async def test_voice_detection(self):
        """Test language detection and voice recommendation."""
        print("🔍 Testing language detection...")
        
        test_texts = [
            ("Bonjour, comment allez-vous?", "French"),
            ("Hello, how are you today?", "English"),
            ("Hola, ¿cómo estás hoy?", "Spanish"),
            ("Guten Tag, wie geht es Ihnen?", "German")
        ]
        
        for text, expected_lang in test_texts:
            try:
                payload = {"text": text}
                async with self.session.post(
                    f"{self.base_url}/api/voices-by-text", 
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        male_count = len(data.get('male_voices', []))
                        female_count = len(data.get('female_voices', []))
                        print(f"✅ {expected_lang}: {male_count} male, {female_count} female voices")
                    else:
                        print(f"❌ Language detection failed for {expected_lang}: {response.status}")
                        return False
            except Exception as e:
                print(f"❌ Language detection error for {expected_lang}: {e}")
                return False
        
        return True
    
    async def test_tts_generation(self, play_audio=False):
        """Test TTS audio generation."""
        print("🔍 Testing TTS generation...")
        
        test_cases = [
            {
                "text": "Bonjour, ceci est un test de synthèse vocale française.",
                "voice": "fr-FR-DeniseNeural",
                "description": "French female voice"
            },
            {
                "text": "Hello, this is an English text-to-speech test.",
                "voice": "en-US-AriaNeural", 
                "description": "English female voice"
            }
        ]
        
        for case in test_cases:
            try:
                print(f"   Testing {case['description']}...")
                
                payload = {
                    "text": case["text"],
                    "voice": case["voice"]
                }
                
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/tts",
                    json=payload
                ) as response:
                    generation_time = time.time() - start_time
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        size_kb = len(audio_data) / 1024
                        print(f"   ✅ Generated {size_kb:.1f}KB audio in {generation_time:.2f}s")
                        
                        # Optional audio playback
                        if play_audio and AUDIO_AVAILABLE and audio_data:
                            try:
                                pygame.mixer.init()
                                pygame.mixer.music.load(io.BytesIO(audio_data))
                                pygame.mixer.music.play()
                                print("   🔊 Playing audio...")
                                while pygame.mixer.music.get_busy():
                                    await asyncio.sleep(0.1)
                                print("   ✅ Audio playback completed")
                            except Exception as audio_error:
                                print(f"   ⚠️  Audio playback failed: {audio_error}")
                    else:
                        print(f"   ❌ TTS generation failed: {response.status}")
                        return False
                        
            except Exception as e:
                print(f"   ❌ TTS generation error: {e}")
                return False
        
        return True
    
    async def test_performance(self):
        """Test service performance."""
        print("🔍 Testing performance...")
        
        # Test concurrent requests
        concurrent_tasks = []
        test_payload = {
            "text": "Performance test text.",
            "voice": "en-US-AriaNeural"
        }
        
        start_time = time.time()
        
        for i in range(5):  # 5 concurrent requests
            task = self.session.post(
                f"{self.base_url}/api/tts",
                json=test_payload
            )
            concurrent_tasks.append(task)
        
        try:
            responses = await asyncio.gather(*concurrent_tasks)
            total_time = time.time() - start_time
            
            success_count = sum(1 for r in responses if r.status == 200)
            print(f"✅ {success_count}/5 concurrent requests succeeded in {total_time:.2f}s")
            
            # Close responses
            for response in responses:
                response.close()
                
            return success_count == 5
            
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    async def run_all_tests(self, play_audio=False):
        """Run all tests."""
        print(f"🚀 Starting TTS service tests for {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Status Check", self.test_status), 
            ("Voice Listing", self.test_voices),
            ("Language Detection", self.test_voice_detection),
            ("TTS Generation", lambda: self.test_tts_generation(play_audio)),
            ("Performance", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Service is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the service.")
            return False


async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test TTS service")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Base URL of the TTS service"
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Enable audio playback (requires pygame)"
    )
    
    args = parser.parse_args()
    
    if args.audio and not AUDIO_AVAILABLE:
        print("❌ Audio playback requested but pygame not available")
        return False
    
    async with TTSTestClient(args.url) as client:
        success = await client.run_all_tests(play_audio=args.audio)
        return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)