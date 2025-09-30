"""
Script simple pour créer un utilisateur et tester l'authentification
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def create_user_via_api():
    """Créer un utilisateur via l'API d'inscription"""
    
    print("👤 Création d'un utilisateur de test via API...")
    
    # Données de l'utilisateur
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Utilisateur Test"
    }
    
    try:
        # Inscription
        print("📝 Inscription en cours...")
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inscription réussie !")
            print(f"   📧 Email: {user_data['email']}")
            print(f"   🔑 Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Inscription échouée: {response.status_code}")
            print(f"   Détails: {response.text}")
            return None
            
    except requests.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur est démarré avec: python saas_app.py")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def login_user():
    """Se connecter avec l'utilisateur de test"""
    
    print("\n🔐 Connexion utilisateur...")
    
    login_data = {
        "email": "test@example.com", 
        "password": "Test123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion réussie !")
            print(f"   🔑 Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Connexion échouée: {response.status_code}")
            print(f"   Détails: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_api_with_token(token):
    """Tester l'API avec le token"""
    
    print(f"\n🧪 Test de l'API avec authentification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test des statistiques d'usage
    try:
        response = requests.get(f"{BASE_URL}/api/v1/saas/usage", headers=headers)
        if response.status_code == 200:
            usage = response.json()
            print(f"✅ Statistiques récupérées :")
            print(f"   Plan: {usage['tier']}")
            print(f"   Caractères utilisés: {usage['chars_used_this_month']:,}")
            print(f"   Limite: {usage['chars_limit']:,}")
        else:
            print(f"❌ Erreur statistiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test API: {e}")

def main():
    """Point d'entrée principal"""
    
    print("🚀 Script de test utilisateur TTS SaaS")
    print("=" * 50)
    
    # Tenter de se connecter d'abord (si l'utilisateur existe déjà)
    token = login_user()
    
    if not token:
        # Créer l'utilisateur s'il n'existe pas
        token = create_user_via_api()
    
    if token:
        # Tester l'API
        test_api_with_token(token)
        
        print(f"\n🌐 Accès au dashboard :")
        print(f"   1. Ouvrez : {BASE_URL}/dashboard")
        print(f"   2. Utilisez le token : {token[:50]}...")
        print(f"\n📖 Documentation API :")
        print(f"   Ouvrez : {BASE_URL}/docs")
        
        # Sauvegarder le token pour tests futurs
        with open("auth_token.txt", "w") as f:
            f.write(token)
        print(f"\n💾 Token sauvegardé dans auth_token.txt")
        
        return True
    else:
        print(f"\n❌ Impossible de créer ou connecter l'utilisateur")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 Utilisateur de test prêt ! Vous pouvez maintenant utiliser l'API SaaS.")
    else:
        print(f"\n💡 Assurez-vous que le serveur est démarré et réessayez.")