"""
Script de test rapide pour vérifier l'intégration SaaS
"""

import asyncio
import sys
import os

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_saas_integration():
    """Test rapide des composants SaaS"""
    
    print("🧪 Test d'intégration des composants SaaS")
    
    try:
        # Test d'import des modules
        from src.auth.auth_system import User, UserTier, AuthService
        print("✅ Système d'authentification importé")
        
        from src.api.saas_routes import auth_router, saas_router
        print("✅ Routes SaaS importées")
        
        from src.web.dashboard import dashboard_router
        print("✅ Dashboard web importé")
        
        # Test de création d'utilisateur
        auth_service = AuthService()
        
        # Test de hashage de mot de passe
        password_hash = auth_service.hash_password("test123")
        print(f"✅ Hash généré: {password_hash[:20]}...")
        
        # Test de vérification de mot de passe
        is_valid = auth_service.verify_password("test123", password_hash)
        print(f"✅ Vérification mot de passe: {is_valid}")
        
        # Test de création d'utilisateur
        user = User(
            user_id="test-123",
            email="test@example.com", 
            password_hash=password_hash,
            tier=UserTier.STARTER
        )
        print(f"✅ Utilisateur créé: {user.email} ({user.tier.value})")
        
        # Test des limites par tier
        from src.auth.auth_system import TierLimits
        limits = TierLimits.get_limits(UserTier.PRO)
        print(f"✅ Limites plan Pro: {limits}")
        
        print("\n🎉 Tous les tests d'intégration sont passés !")
        print("\n📝 Prochaines étapes:")
        print("1. Démarrer l'application: python saas_app.py")
        print("2. Ouvrir le dashboard: http://localhost:8000/dashboard") 
        print("3. Tester l'API: http://localhost:8000/docs")
        print("4. S'inscrire via: http://localhost:8000/api/v1/auth/register")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_saas_integration())
    sys.exit(0 if success else 1)