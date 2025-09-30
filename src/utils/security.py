"""Security utilities and middleware."""

import hashlib
import time
from typing import Dict, List
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for the given identifier."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) >= self.max_requests:
            return False
        
        # Add current request
        request_times.append(now)
        return True
    
    def get_reset_time(self, identifier: str) -> float:
        """Get time when the rate limit will reset for the identifier."""
        request_times = self.requests[identifier]
        if not request_times:
            return 0
        return request_times[0] + self.window_seconds


class SecurityValidator:
    """Security validation utilities."""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input to prevent injection attacks."""
        if not text:
            return ""
        
        # Remove or escape potentially dangerous characters
        dangerous_patterns = [
            '<script', '</script>', '<iframe', '</iframe>',
            'javascript:', 'data:', 'vbscript:', 'onload=',
            'onerror=', 'onclick=', 'onmouseover='
        ]
        
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_voice_name(voice: str) -> bool:
        """Validate voice name format."""
        if not voice:
            return False
        
        # Voice names should follow pattern: language-region-VoiceName
        import re
        pattern = r'^[a-z]{2}-[A-Z]{2}-[A-Za-z0-9]+$'
        return bool(re.match(pattern, voice))
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


def create_rate_limit_middleware(rate_limiter: RateLimiter):
    """Create rate limiting middleware."""
    
    async def rate_limit_middleware(request: Request, call_next):
        """Rate limiting middleware."""
        client_ip = SecurityValidator.get_client_ip(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/status"]:
            return await call_next(request)
        
        if not rate_limiter.is_allowed(client_ip):
            reset_time = rate_limiter.get_reset_time(client_ip)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(int(reset_time - time.time())),
                    "X-RateLimit-Limit": str(rate_limiter.max_requests),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        return await call_next(request)
    
    return rate_limit_middleware


@asynccontextmanager
async def security_context():
    """Security context manager for resource cleanup."""
    try:
        yield
    except Exception as e:
        logger.error(f"Security context error: {e}")
        raise
    finally:
        # Cleanup if needed
        pass