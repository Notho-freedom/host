"""
Test ultra simple pour créer un utilisateur directement
"""

import sys
import os
sys.path.append('.')

def test_direct_auth():
    """Tester directement le système d'authentification"""
    
    print("🧪 Test direct du système d'authentification")
    print("=" * 50)
    
    try:
        # Import du système d'auth
        from src.auth.auth_system import AuthService, UserTier
        
        # Créer le service
        auth_service = AuthService()
        print("✅ Service d'authentification créé")
        
        # Tester le hashage
        password = "Test123!"
        hashed = auth_service.hash_password(password)
        print(f"✅ Hash généré: {hashed[:30]}...")
        
        # Vérifier le mot de passe
        is_valid = auth_service.verify_password(password, hashed)
        print(f"✅ Vérification: {is_valid}")
        
        # Créer un utilisateur
        import asyncio
        
        async def create_test_user():
            try:
                user = await auth_service.create_user(
                    email="test@example.com",
                    password=password,
                    tier=UserTier.STARTER
                )
                print(f"✅ Utilisateur créé: {user.email}")
                print(f"   ID: {user.user_id}")
                print(f"   Tier: {user.tier}")
                
                # Tester l'authentification
                auth_user = await auth_service.authenticate_user("test@example.com", password)
                if auth_user:
                    print("✅ Authentification réussie")
                    
                    # Créer un token
                    token = auth_service.create_access_token({"sub": auth_user.user_id})
                    print(f"✅ Token créé: {token[:50]}...")
                    
                    return True
                else:
                    print("❌ Authentification échouée")
                    return False
                    
            except Exception as e:
                print(f"❌ Erreur lors de la création: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Exécuter le test async
        success = asyncio.run(create_test_user())
        
        if success:
            print("\n🎉 Test direct réussi !")
            print("✅ Le système d'authentification fonctionne")
            print("✅ Un utilisateur test est créé")
            print("\n🔑 Identifiants:")
            print("   Email: test@example.com")
            print("   Mot de passe: Test123!")
            
            # Sauvegarder les infos pour tests manuels
            with open("user_created.txt", "w") as f:
                f.write("test@example.com\nTest123!\n")
            print("💾 Identifiants sauvegardés dans user_created.txt")
            
            return True
        else:
            return False
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Test direct du système d'authentification")
    print()
    
    success = test_direct_auth()
    
    if success:
        print(f"\n✅ Le système d'authentification fonctionne !")
        print(f"🎯 Maintenant vous pouvez :")
        print(f"   1. Démarrer le serveur: python saas_app.py")
        print(f"   2. Aller sur: http://localhost:8000/dashboard/login")  
        print(f"   3. Se connecter avec: test@example.com / Test123!")
    else:
        print(f"\n❌ Problème avec le système d'authentification")
        print(f"💡 Vérifiez les imports et les dépendances")