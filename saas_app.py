"""
Application TTS SaaS complète avec interface web
Intègre l'API TTS existante avec l'authentification et le dashboard
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
import os

# Import des routes existantes
from src.api.routes import router as tts_router

# Import des nouvelles routes SaaS
from src.api.saas_routes import (
    auth_router, 
    saas_router, 
    billing_router
)

# Import du dashboard web
from src.web.dashboard import dashboard_router

# Import du middleware d'authentification
from src.utils.middleware import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    print("🚀 Démarrage de l'application TTS SaaS...")
    
    # Initialisation des services (Redis, cache, etc.)
    try:
        # Test de connexion Redis si disponible
        from redis import Redis
        redis_client = Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print("✅ Connexion Redis établie")
    except Exception as e:
        print(f"⚠️  Redis non disponible: {e}")
        print("📝 Le système utilisera le cache en mémoire")
    
    yield
    
    print("🛑 Arrêt de l'application TTS SaaS")


# Création de l'application FastAPI
app = FastAPI(
    title="TTS SaaS Platform",
    description="Plateforme de synthèse vocale en tant que service",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware d'authentification personnalisé
app.middleware("http")(auth_middleware)

# Montage des fichiers statiques si le dossier existe
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routes de l'API TTS existante
app.include_router(tts_router, prefix="/api/v1", tags=["TTS"])

# Routes d'authentification SaaS
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# Routes SaaS avec authentification
app.include_router(saas_router, prefix="/api/v1/saas", tags=["SaaS TTS"])

# Routes de facturation
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])

# Interface web (dashboard)
app.include_router(dashboard_router, tags=["Web Dashboard"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec redirection vers la page de login"""
    return RedirectResponse(url="/dashboard/login", status_code=302)

@app.get("/info")
async def api_info():
    """Informations sur l'API"""
    return {
        "message": "Bienvenue sur la plateforme TTS SaaS",
        "version": "1.0.0",
        "endpoints": {
            "login": "/dashboard/login",
            "dashboard": "/dashboard",
            "api_docs": "/docs",
            "api_tts": "/api/v1/tts",
            "saas_tts": "/api/v1/saas/tts",
            "authentication": "/api/v1/auth"
        },
        "features": [
            "Synthèse vocale multilingue",
            "Authentification JWT",
            "Plans d'abonnement flexibles", 
            "Dashboard utilisateur",
            "API REST complète",
            "Rate limiting adaptatif"
        ]
    }


@app.get("/health")
async def health_check():
    """Point de contrôle de santé pour le monitoring"""
    return {
        "status": "healthy",
        "service": "TTS SaaS",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🎯 Lancement du serveur TTS SaaS...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔌 API TTS: http://localhost:8000/api/v1/tts")
    print("💎 SaaS TTS: http://localhost:8000/api/v1/saas/tts")
    
    uvicorn.run(
        "saas_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )