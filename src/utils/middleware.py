"""Application middleware for error handling, monitoring, and authentication."""

import time
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging

from src.models.schemas import ErrorResponse

logger = logging.getLogger(__name__)


async def auth_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware d'authentification pour les routes SaaS
    Laisse passer les routes publiques et vérifie l'auth pour les routes protégées
    """
    
    # Routes publiques qui ne nécessitent pas d'authentification
    public_routes = [
        "/",
        "/health", 
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/tts",  # API TTS originale reste publique
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/static"
    ]
    
    # Vérifier si la route est publique
    path = request.url.path
    if any(path.startswith(route) for route in public_routes):
        response = await call_next(request)
        return response
    
    # Pour les routes protégées, l'authentification sera gérée par les dépendances FastAPI
    response = await call_next(request)
    return response


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """Global error handling middleware."""
    
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Add request ID to logger context
    logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")
    
    try:
        response = await call_next(request)
        
        # Log successful requests
        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Completed in {duration:.3f}s with status {response.status_code}"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
        
    except HTTPException as e:
        # Handle FastAPI HTTP exceptions
        duration = time.time() - start_time
        logger.warning(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"HTTP Exception {e.status_code}: {e.detail} (took {duration:.3f}s)"
        )
        
        error_response = ErrorResponse(
            error=e.detail,
            code=f"HTTP_{e.status_code}"
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content=error_response.dict(),
            headers={"X-Request-ID": request_id}
        )
        
    except Exception as e:
        # Handle unexpected exceptions
        duration = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Unhandled exception: {str(e)} (took {duration:.3f}s)",
            exc_info=True
        )
        
        error_response = ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred" if not logger.isEnabledFor(logging.DEBUG) else str(e),
            code="INTERNAL_ERROR"
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.dict(),
            headers={"X-Request-ID": request_id}
        )


async def performance_middleware(request: Request, call_next: Callable) -> Response:
    """Performance monitoring middleware."""
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(round(duration, 3))
    
    # Log slow requests
    if duration > 5.0:  # Log requests taking more than 5 seconds
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {duration:.3f}s"
        )
    
    return response


async def health_check_middleware(request: Request, call_next: Callable) -> Response:
    """Health check and monitoring middleware."""
    
    # Quick health check endpoint
    if request.url.path == "/health":
        try:
            # Perform basic health checks here
            from src.services.tts_service import tts_service
            
            # Check if we can get voices (basic service health)
            voices = await tts_service.get_all_voices()
            
            health_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "checks": {
                    "tts_service": "ok",
                    "voices_available": len(voices) > 0
                }
            }
            
            return JSONResponse(content=health_data)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
            health_data = {
                "status": "unhealthy",
                "timestamp": time.time(),
                "checks": {
                    "tts_service": "error",
                    "error": str(e)
                }
            }
            
            return JSONResponse(
                status_code=503,
                content=health_data
            )
    
    return await call_next(request)