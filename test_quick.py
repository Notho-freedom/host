"""
Test simple des endpoints pour vérifier que le serveur fonctionne
"""

import requests
import json

def test_endpoints():
    """Tester les endpoints de base"""
    
    print("🧪 Test des endpoints TTS SaaS")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Page d'accueil (doit rediriger vers login)
    print("\n1️⃣ Test page d'accueil...")
    try:
        response = requests.get(base_url, allow_redirects=False)
        if response.status_code == 302:
            print(f"✅ Redirection détectée vers: {response.headers.get('location', 'inconnu')}")
        else:
            print(f"⚠️  Status inattendu: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 2: Page de login
    print("\n2️⃣ Test page de login...")
    try:
        response = requests.get(f"{base_url}/dashboard/login")
        if response.status_code == 200:
            print("✅ Page de login accessible")
            if "TTS SaaS" in response.text:
                print("✅ Contenu de la page correct")
            else:
                print("⚠️  Contenu de la page inattendu")
        else:
            print(f"❌ Page de login inaccessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 3: API docs
    print("\n3️⃣ Test documentation API...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentation API accessible")
        else:
            print(f"❌ Documentation API inaccessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Health check
    print("\n4️⃣ Test health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service en santé: {health_data['status']}")
        else:
            print(f"❌ Health check échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 5: Inscription d'un utilisateur
    print("\n5️⃣ Test inscription utilisateur...")
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Utilisateur Test"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Inscription réussie")
            print(f"   Token reçu: {data.get('access_token', 'Non trouvé')[:30]}...")
            
            # Sauvegarder le token
            with open("user_token.txt", "w") as f:
                f.write(data.get('access_token', ''))
            print("💾 Token sauvegardé dans user_token.txt")
            return True
        else:
            print(f"❌ Inscription échouée: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détails: {error_data.get('detail', 'Erreur inconnue')}")
            except:
                print(f"   Réponse: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Erreur inscription: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("🚀 Test de la plateforme TTS SaaS")
    print("💡 Assurez-vous que le serveur est démarré avec: python saas_app.py")
    print()
    
    success = test_endpoints()
    
    if success:
        print("\n🎉 Tests réussis ! Votre plateforme SaaS fonctionne.")
        print("\n🌐 Accès:")
        print("├── Login: http://localhost:8000/dashboard/login")
        print("├── Dashboard: http://localhost:8000/dashboard (après connexion)")
        print("├── API Docs: http://localhost:8000/docs")
        print("└── Health: http://localhost:8000/health")
        
        print("\n🔑 Identifiants de test:")
        print("├── Email: test@example.com")
        print("└── Mot de passe: Test123!")
    else:
        print("\n❌ Certains tests ont échoué.")
        print("💡 Vérifiez que le serveur est bien démarré.")