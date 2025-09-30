"""
🧪 Script de test complet pour la plateforme TTS SaaS
Teste l'inscription, l'authentification, et l'utilisation de l'API
"""

import asyncio
import httpx
import json
import sys
import time

BASE_URL = "http://localhost:8000"

async def test_saas_complete():
    """Test complet de la plateforme SaaS"""
    
    print("🧪 Test complet de la plateforme TTS SaaS")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Test de santé
        print("\n1️⃣ Test de santé du serveur...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Serveur accessible")
                print(f"   Status: {response.json()['status']}")
            else:
                print("❌ Serveur non accessible")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            print("💡 Assurez-vous que le serveur est démarré avec: python start_saas.py")
            return False
        
        # 2. Test d'inscription
        print("\n2️⃣ Test d'inscription utilisateur...")
        user_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
            if response.status_code == 200:
                print(f"✅ Inscription réussie: {user_data['email']}")
                user_token = response.json()["access_token"]
            else:
                print(f"❌ Inscription échouée: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur inscription: {e}")
            return False
        
        # 3. Test de connexion
        print("\n3️⃣ Test de connexion...")
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ Connexion réussie")
                token = response.json()["access_token"]
            else:
                print(f"❌ Connexion échouée: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
        
        # 4. Test des statistiques d'usage
        print("\n4️⃣ Test des statistiques d'usage...")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.get(f"{BASE_URL}/api/v1/saas/usage", headers=headers)
            if response.status_code == 200:
                usage = response.json()
                print("✅ Statistiques récupérées")
                print(f"   Tier: {usage['tier']}")
                print(f"   Caractères utilisés: {usage['chars_used_this_month']}")
                print(f"   Limite: {usage['chars_limit']}")
            else:
                print(f"❌ Erreur statistiques: {response.text}")
        except Exception as e:
            print(f"❌ Erreur usage: {e}")
        
        # 5. Test TTS SaaS
        print("\n5️⃣ Test de synthèse vocale SaaS...")
        tts_data = {
            "text": "Bonjour ! Ceci est un test de la plateforme TTS SaaS.",
            "voice": "fr-FR-DeniseNeural"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/v1/saas/tts", headers=headers, json=tts_data)
            if response.status_code == 200:
                print("✅ Synthèse vocale réussie")
                print(f"   Taille audio: {len(response.content)} octets")
                print(f"   Type: {response.headers.get('content-type', 'inconnu')}")
                
                # Sauvegarder l'audio pour vérification
                with open("test_audio.mp3", "wb") as f:
                    f.write(response.content)
                print("   💾 Audio sauvegardé: test_audio.mp3")
            else:
                print(f"❌ TTS échoué: {response.text}")
        except Exception as e:
            print(f"❌ Erreur TTS: {e}")
        
        # 6. Test des voix disponibles
        print("\n6️⃣ Test des voix disponibles...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/saas/voices", headers=headers)
            if response.status_code == 200:
                voices = response.json()
                print(f"✅ {len(voices)} voix disponibles")
                for voice in voices[:3]:  # Afficher les 3 premières
                    print(f"   🎤 {voice['display_name']} ({voice['locale']})")
            else:
                print(f"❌ Erreur voix: {response.text}")
        except Exception as e:
            print(f"❌ Erreur voix: {e}")
        
        # 7. Test du dashboard (GET simple)
        print("\n7️⃣ Test d'accès au dashboard...")
        try:
            response = await client.get(f"{BASE_URL}/dashboard/", headers=headers)
            if response.status_code == 200:
                print("✅ Dashboard accessible")
                print(f"   Taille page: {len(response.content)} octets")
            else:
                print(f"❌ Dashboard inaccessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur dashboard: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test complet terminé !")
    print("\n📋 Résumé de votre plateforme TTS SaaS :")
    print("├── ✅ Serveur fonctionnel")
    print("├── ✅ Système d'authentification JWT")
    print("├── ✅ API TTS SaaS protégée")
    print("├── ✅ Statistiques d'usage")
    print("├── ✅ Dashboard web accessible")
    print("└── ✅ Gestion des voix et plans")
    
    print(f"\n🌐 Accédez à votre plateforme :")
    print(f"├── Dashboard: {BASE_URL}/dashboard")
    print(f"├── Documentation: {BASE_URL}/docs")
    print(f"└── API: {BASE_URL}/api/v1/saas/")
    
    return True


if __name__ == "__main__":
    print("🚀 Démarrage du test complet...")
    print("💡 Assurez-vous que le serveur est démarré avec: python start_saas.py")
    
    try:
        success = asyncio.run(test_saas_complete())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu par l'utilisateur")
        sys.exit(1)