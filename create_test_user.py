"""
Script pour créer un utilisateur de test
Permet de tester rapidement l'authentification sans passer par l'inscription
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def create_test_user():
    """Créer un utilisateur de test"""
    
    print("👤 Création d'un utilisateur de test...")
    
    try:
        from src.auth.auth_system import User, UserTier, AuthService
        
        # Service d'authentification
        auth_service = AuthService()
        
        # Données de l'utilisateur de test
        test_email = "test@example.com"
        test_password = "Test123!"
        
        # Hasher le mot de passe
        password_hash = auth_service.hash_password(test_password)
        
        # Créer l'utilisateur
        test_user = User(
            user_id="test-user-001",
            email=test_email,
            tier=UserTier.STARTER,  # Plan Starter pour tester les fonctionnalités
            chars_used_this_month=5000,  # Quelques caractères déjà utilisés
            created_at=datetime.now()
        )
        
        # Stocker dans le "cache" utilisateur (simulation base de données)
        user_data = {
            "user_id": test_user.user_id,
            "email": test_user.email,
            "password_hash": password_hash,
            "tier": test_user.tier.value,
            "chars_used_this_month": test_user.chars_used_this_month,
            "created_at": test_user.created_at.isoformat()
        }
        
        # Stocker dans la "base de données" simulée
        auth_service.users_db[test_user.user_id] = user_data
        auth_service.users_db[f"email:{test_user.email}"] = test_user.user_id
        
        print(f"✅ Utilisateur de test créé avec succès !")
        print(f"   📧 Email: {test_email}")
        print(f"   🔑 Mot de passe: {test_password}")
        print(f"   🎯 Plan: {test_user.tier.value.title()}")
        print(f"   📊 Usage: {test_user.chars_used_this_month:,} caractères utilisés")
        
        # Générer un token JWT pour test direct
        token = auth_service.create_access_token({"sub": test_user.user_id})
        
        print(f"\n🔗 Token JWT (pour tests API):")
        print(f"   {token[:50]}...")
        
        print(f"\n🧪 Tests de connexion:")
        print(f"   curl -X POST http://localhost:8000/api/v1/auth/login \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"email\": \"{test_email}\", \"password\": \"{test_password}\"}}'")
        
        print(f"\n🌐 Accès dashboard:")
        print(f"   1. Aller sur http://localhost:8000/api/v1/auth/login")
        print(f"   2. Se connecter avec {test_email} / {test_password}")
        print(f"   3. Utiliser le token pour accéder au dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_login_helper():
    """Créer un helper de connexion simple"""
    
    login_script = '''
import requests
import json

# Données de connexion
email = "test@example.com"
password = "Test123!"
base_url = "http://localhost:8000"

# Connexion
login_data = {"email": email, "password": password}
response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)

if response.status_code == 200:
    data = response.json()
    token = data["access_token"]
    print(f"✅ Connexion réussie !")
    print(f"🔑 Token: {token}")
    
    # Test API avec token
    headers = {"Authorization": f"Bearer {token}"}
    usage_response = requests.get(f"{base_url}/api/v1/saas/usage", headers=headers)
    
    if usage_response.status_code == 200:
        usage = usage_response.json()
        print(f"📊 Usage: {usage}")
    
else:
    print(f"❌ Échec connexion: {response.text}")
'''
    
    with open("login_test.py", "w", encoding="utf-8") as f:
        f.write(login_script)
    
    print("📝 Script de test créé: login_test.py")


if __name__ == "__main__":
    print("🚀 Setup utilisateur de test pour TTS SaaS")
    print("=" * 50)
    
    success = asyncio.run(create_test_user())
    
    if success:
        create_login_helper()
        print("\n🎉 Setup terminé ! Utilisateur de test prêt à l'emploi.")
        print("\n💡 Pour tester:")
        print("   1. Démarrez le serveur: python saas_app.py")
        print("   2. Testez la connexion: python login_test.py")
    
    sys.exit(0 if success else 1)