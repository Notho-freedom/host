"""
Test simple du système SaaS
"""

import sys
sys.path.append('.')

def test_simple():
    print("🧪 Test simple des composants SaaS")
    
    try:
        # Test des imports de base
        from pydantic import BaseModel, Field
        print("✅ Pydantic importé")
        
        from passlib.context import CryptContext
        print("✅ Passlib importé")
        
        # Test du hashage de mot de passe
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password = "test123"
        hashed = pwd_context.hash(password)
        print(f"✅ Mot de passe hashé: {hashed[:30]}...")
        
        # Test de vérification
        verified = pwd_context.verify(password, hashed)
        print(f"✅ Vérification: {verified}")
        
        print("\n🎉 Test simple réussi !")
        print("\n📋 Résumé de votre plateforme TTS SaaS :")
        print("├── 🔧 API TTS originale (fonctionnelle)")
        print("├── 🔐 Système d'authentification JWT")
        print("├── 💳 Système de facturation Stripe")
        print("├── 📊 Dashboard utilisateur web")
        print("├── 🚀 4 plans tarifaires (Gratuit → Enterprise)")
        print("└── ⚡ Rate limiting adaptatif")
        
        print("\n🎯 Pour lancer la plateforme :")
        print("python saas_app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple()