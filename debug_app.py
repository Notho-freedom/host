"""
Version simplifiée pour tester les routes d'authentification
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routes
from src.api.saas_routes import auth_router

# Création de l'application
app = FastAPI(title="TTS SaaS Debug", description="Test des routes d'auth")

# Configuration CORS  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes d'authentification
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "Debug TTS SaaS", "auth_endpoints": ["/api/v1/auth/register", "/api/v1/auth/login"]}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "debug"}

if __name__ == "__main__":
    import uvicorn
    print("🔍 Démarrage du serveur debug...")
    print("📋 Routes disponibles:")
    print("   GET  / (informations)")
    print("   GET  /docs (documentation)")
    print("   POST /api/v1/auth/register")
    print("   POST /api/v1/auth/login")
    
    uvicorn.run(
        "debug_app:app",
        host="127.0.0.1",
        port=8001,  # Port différent pour éviter les conflits
        reload=False,  # Pas de reload pour éviter les problèmes
        log_level="info"
    )