"""Modern FastAPI application with enhanced architecture."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Import configurations and utilities
from src.core.config import settings
from src.utils.logging import setup_logging
from src.utils.security import RateLimiter, create_rate_limit_middleware
from src.utils.middleware import (
    error_handler_middleware, 
    performance_middleware, 
    health_check_middleware
)
from src.api.routes import router


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Configuration: Debug={settings.debug}, Environment=Production")
    
    try:
        # Initialize services
        from src.services.tts_service import tts_service
        
        # Warm up cache by loading voices
        logger.info("Warming up voice cache...")
        voices = await tts_service.get_all_voices()
        logger.info(f"Loaded {len(voices)} voices into cache")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Enhanced Text-to-Speech API with Microsoft Edge TTS",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)

# Rate Limiting
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window
)

# Add middleware in correct order (reverse order of execution)
app.middleware("http")(create_rate_limit_middleware(rate_limiter))
app.middleware("http")(performance_middleware)
app.middleware("http")(health_check_middleware)
app.middleware("http")(error_handler_middleware)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return JSONResponse(content={
        "service": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs_url": "/docs" if settings.debug else "disabled",
        "health_url": "/health"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint (handled by middleware)."""
    # This will be intercepted by health_check_middleware
    pass


def create_app() -> FastAPI:
    """Application factory."""
    return app


def run_server(
    host: str = None,
    port: int = None,
    reload: bool = None,
    log_level: str = None
):
    """Run the application server."""
    
    server_config = {
        "app": "main:app",
        "host": host or settings.host,
        "port": port or settings.port,
        "reload": reload if reload is not None else settings.reload,
        "log_level": (log_level or settings.log_level).lower(),
        "access_log": settings.debug,
        "server_header": False,  # Hide server header for security
        "date_header": False     # Hide date header for security
    }
    
    logger.info(f"Starting server on http://{server_config['host']}:{server_config['port']}")
    uvicorn.run(**server_config)


if __name__ == "__main__":
    run_server()