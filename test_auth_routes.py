"""
Test simple pour vérifier les routes d'authentification
"""

import requests
import json

def test_auth_routes():
    """Tester les routes d'authentification"""
    
    print("🧪 Test des routes d'authentification")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Vérifier que l'API docs liste les routes
    print("\n1️⃣ Vérification des routes dans l'API...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentation API accessible")
        
        # Vérifier les routes via OpenAPI
        openapi_response = requests.get(f"{base_url}/openapi.json")
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            paths = openapi_data.get("paths", {})
            
            auth_routes = [path for path in paths.keys() if "auth" in path]
            print(f"🔍 Routes d'auth trouvées: {auth_routes}")
            
            if "/api/v1/auth/register" in paths:
                print("✅ Route d'inscription trouvée")
            else:
                print("❌ Route d'inscription manquante")
                
            if "/api/v1/auth/login" in paths:
                print("✅ Route de connexion trouvée")  
            else:
                print("❌ Route de connexion manquante")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Tenter l'inscription
    print("\n2️⃣ Test d'inscription...")
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data)
        print(f"📍 Status code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Inscription réussie !")
            print(f"🔑 Token reçu: {data.get('access_token', 'Non trouvé')[:30]}...")
            return data.get('access_token')
        else:
            print("❌ Inscription échouée")
            
    except Exception as e:
        print(f"❌ Erreur inscription: {e}")
    
    # Test 3: Tenter la connexion
    print("\n3️⃣ Test de connexion...")
    login_data = {
        "email": "test@example.com",
        "password": "Test123!"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        print(f"📍 Status code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie !")
            print(f"🔑 Token reçu: {data.get('access_token', 'Non trouvé')[:30]}...")
            return data.get('access_token')
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Test ciblé des routes d'authentification")
    print("💡 Assurez-vous que le serveur tourne : python saas_app.py")
    print()
    
    token = test_auth_routes()
    
    if token:
        print(f"\n🎉 Authentification fonctionnelle !")
        print(f"🔑 Token disponible pour tests API")
    else:
        print(f"\n❌ Problème avec l'authentification")
        print(f"💡 Vérifiez les logs du serveur pour plus d'infos")