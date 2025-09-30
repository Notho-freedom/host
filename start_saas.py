"""
🚀 Lanceur pour la plateforme TTS SaaS
Démarre l'application avec toutes les fonctionnalités
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Affiche la bannière de démarrage"""
    print("""
████████╗████████╗███████╗    ███████╗ █████╗  █████╗ ███████╗
╚══██╔══╝╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝
   ██║      ██║   ███████╗    ███████╗███████║███████║███████╗
   ██║      ██║   ╚════██║    ╚════██║██╔══██║██╔══██║╚════██║
   ██║      ██║   ███████║    ███████║██║  ██║██║  ██║███████║
   ╚═╝      ╚═╝   ╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
   
           🎯 Plateforme de Synthèse Vocale as a Service
                        Version 1.0.0
    """)

def check_dependencies():
    """Vérifie les dépendances critiques"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'passlib',
        'redis',
        'jose',
        'jinja2'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package}")
    
    if missing:
        print(f"\n⚠️  Dépendances manquantes: {', '.join(missing)}")
        print("💡 Installez-les avec: pip install " + " ".join(missing))
        return False
    
    print("✅ Toutes les dépendances sont installées !")
    return True

def check_redis():
    """Vérifie la connexion Redis (optionnelle)"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis connecté (rate limiting activé)")
        return True
    except Exception:
        print("⚠️  Redis non disponible (cache mémoire utilisé)")
        return False

def start_application():
    """Démarre l'application FastAPI"""
    print("\n🚀 Démarrage de la plateforme TTS SaaS...")
    print("=" * 60)
    
    try:
        # Lancer l'application avec uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "saas_app:app",
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ]
        
        print("📡 Serveur démarré sur:")
        print("   🌐 Interface: http://localhost:8000")
        print("   📊 Dashboard: http://localhost:8000/dashboard") 
        print("   📖 API Docs: http://localhost:8000/docs")
        print("   🔌 API TTS: http://localhost:8000/api/v1/tts")
        print("   💎 SaaS TTS: http://localhost:8000/api/v1/saas/tts")
        print("=" * 60)
        
        # Démarrer le serveur
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de l'application demandé")
        print("👋 Merci d'avoir utilisé TTS SaaS !")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

def main():
    """Point d'entrée principal"""
    print_banner()
    
    # Vérifications pré-démarrage
    if not check_dependencies():
        print("\n❌ Impossible de démarrer sans les dépendances requises")
        return False
    
    check_redis()
    
    # Informations sur la plateforme
    print(f"\n📋 Configuration de la plateforme:")
    print(f"├── 📂 Répertoire: {os.getcwd()}")
    print(f"├── 🐍 Python: {sys.version.split()[0]}")
    print(f"├── 🔐 Authentification: JWT + bcrypt")
    print(f"├── 💳 Facturation: Stripe intégré")
    print(f"├── 🌐 Interface: Dashboard web")
    print(f"└── ⚡ Rate limiting: Redis/mémoire")
    
    print(f"\n💰 Plans tarifaires disponibles:")
    print(f"├── 🆓 Gratuit: 1K caractères/mois")
    print(f"├── 🚀 Starter: 10€/mois - 50K caractères")
    print(f"├── 💼 Pro: 49€/mois - 500K caractères")
    print(f"└── 🏢 Enterprise: 199€/mois - 5M caractères")
    
    # Démarrage
    input("\n🎯 Appuyez sur Entrée pour démarrer le serveur...")
    return start_application()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)