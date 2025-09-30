# 🎯 TTS SaaS Platform - Documentation Complète

## 🚀 Vue d'ensemble

Plateforme de **Synthèse Vocale as a Service** (TTS SaaS) complète avec authentification, facturation, dashboard web et API REST. Transformez votre service TTS en business rentable avec un système d'abonnements multi-niveaux.

## ✨ Fonctionnalités

### 🔧 API TTS
- **Synthèse vocale multilingue** avec edge-tts
- **Détection automatique de langue** avec langdetect  
- **Streaming audio** en temps réel
- **Support multi-formats** (MP3, WAV, etc.)

### 🔐 Système d'Authentification
- **JWT Authentication** sécurisé
- **Hashage bcrypt** des mots de passe
- **Gestion des sessions** utilisateur
- **API Key** personnalisée par utilisateur

### 💰 Modèle d'Affaires SaaS
- **4 plans tarifaires** flexibles
- **Rate limiting** adaptatif par plan
- **Facturation Stripe** intégrée
- **Tracking d'usage** en temps réel

### 📊 Dashboard Web
- **Interface utilisateur** intuitive
- **Statistiques d'usage** en temps réel
- **Gestion des abonnements**
- **Documentation API** intégrée

## 📋 Plans Tarifaires

| Plan | Prix | Caractères/mois | Requêtes/min | Fonctionnalités |
|------|------|-----------------|--------------|-----------------|
| **Gratuit** | 0€ | 1,000 | 5 | Accès de base |
| **Starter** | 10€ | 50,000 | 20 | API complète, Support email |
| **Pro** | 49€ | 500,000 | 100 | Voix custom, Support prioritaire |
| **Enterprise** | 199€ | 5,000,000 | 500 | SLA 99.9%, Support 24/7 |

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Redis (optionnel, pour rate limiting)
- Compte Stripe (pour la facturation)

### Installation rapide
```bash
# 1. Cloner le projet
git clone <votre-repo>
cd tts-saas-platform

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# 4. Démarrer la plateforme
python start_saas.py
```

### Dépendances principales
```txt
fastapi>=0.104.1          # Framework web moderne
uvicorn[standard]>=0.24.0 # Serveur ASGI
pydantic>=2.4.0           # Validation de données
redis>=5.0.0              # Cache et rate limiting
python-jose[cryptography] # JWT tokens
passlib[bcrypt]           # Hashage sécurisé
stripe>=7.8.0             # Paiements
jinja2>=3.1.2            # Templates web
edge-tts>=6.1.8          # Synthèse vocale
langdetect>=1.0.9        # Détection de langue
```

## 🚀 Démarrage

### Méthode 1: Script de démarrage
```bash
python start_saas.py
```

### Méthode 2: Démarrage direct
```bash
uvicorn saas_app:app --host 0.0.0.0 --port 8000 --reload
```

### Accès à la plateforme
- **🌐 Interface:** http://localhost:8000
- **📊 Dashboard:** http://localhost:8000/dashboard  
- **📖 API Docs:** http://localhost:8000/docs
- **🔌 API TTS:** http://localhost:8000/api/v1/tts
- **💎 SaaS TTS:** http://localhost:8000/api/v1/saas/tts

## 🧪 Tests

### Test complet de la plateforme
```bash
# Démarrer le serveur dans un terminal
python start_saas.py

# Dans un autre terminal, lancer les tests
python test_saas_complete.py
```

### Tests unitaires existants
```bash
pytest                          # Tous les tests
pytest tests/test_api.py       # Tests API
pytest tests/test_services.py  # Tests services
pytest --cov=src --cov-report=html  # Avec couverture
```

## 📖 Documentation API

### Authentification

#### Inscription
```bash
POST /api/v1/auth/register
{
  \"email\": \"user@example.com\",
  \"password\": \"SecurePass123!\",
  \"full_name\": \"John Doe\"
}
```

#### Connexion
```bash
POST /api/v1/auth/login
{
  \"email\": \"user@example.com\",
  \"password\": \"SecurePass123!\"
}
# Retourne: {\"access_token\": \"eyJ...\", \"token_type\": \"bearer\"}
```

### API TTS SaaS

#### Synthèse vocale
```bash
POST /api/v1/saas/tts
Authorization: Bearer <token>
{
  \"text\": \"Bonjour, ceci est un test de synthèse vocale.\",
  \"voice\": \"fr-FR-DeniseNeural\",
  \"rate\": \"+10%\"
}
# Retourne: Fichier audio MP3
```

#### Statistiques d'usage
```bash
GET /api/v1/saas/usage
Authorization: Bearer <token>
# Retourne: Usage actuel et limites
```

#### Voix disponibles
```bash
GET /api/v1/saas/voices  
Authorization: Bearer <token>
# Retourne: Liste des voix selon le plan
```

## 🔧 Configuration

### Variables d'environnement (.env)
```env
# Application
DEBUG=True
SECRET_KEY=your-super-secret-key-here

# Redis (optionnel)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Stripe (pour la facturation)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# TTS
DEFAULT_VOICE=fr-FR-DeniseNeural
AUDIO_FORMAT=mp3
```

## 🏗️ Architecture

```
tts-saas-platform/
├── saas_app.py              # Application principale
├── start_saas.py            # Script de démarrage
├── requirements.txt         # Dépendances
├── pytest.ini              # Configuration tests
├── docs/
│   └── saas-monetization-plan.md
├── src/
│   ├── api/
│   │   ├── routes.py        # API TTS originale
│   │   └── saas_routes.py   # API SaaS avec auth
│   ├── auth/
│   │   └── auth_system.py   # Système d'authentification
│   ├── core/
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Modèles de données
│   ├── services/
│   │   └── tts_service.py   # Service TTS
│   ├── utils/
│   │   ├── cache.py         # Cache Redis/mémoire
│   │   ├── middleware.py    # Middlewares
│   │   └── security.py      # Sécurité JWT
│   └── web/
│       ├── dashboard.py     # Routes dashboard
│       └── templates/       # Templates Jinja2
│           ├── dashboard.html
│           ├── api_docs.html
│           └── billing.html
└── tests/
    ├── conftest.py          # Configuration tests
    ├── test_api.py          # Tests API
    ├── test_integration.py  # Tests d'intégration
    └── test_services.py     # Tests services
```

## 💳 Intégration Stripe

### Configuration des webhooks
```bash
# URL du webhook
https://yourdomain.com/api/v1/billing/webhook

# Événements à écouter
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_succeeded
- invoice.payment_failed
```

### Plans Stripe recommandés
```python
# Créer les plans dans Stripe Dashboard
stripe.Product.create(name=\"TTS SaaS Starter\")
stripe.Price.create(
    product=\"prod_...\",
    unit_amount=1000,  # 10€ en centimes
    currency=\"eur\",
    recurring={\"interval\": \"month\"}
)
```

## 📊 Monitoring & Analytics

### Métriques clés à surveiller
- **Usage par utilisateur** (caractères/mois)
- **Taux de conversion** (Gratuit → Payant)
- **Churn rate** (désabonnements)
- **Revenue per user** (ARPU)
- **API response time**
- **Erreurs et échecs**

### Logs structurés
```python
# Les logs incluent automatiquement
{
  \"timestamp\": \"2024-01-15T10:30:00Z\",
  \"level\": \"INFO\", 
  \"user_id\": \"user_123\",
  \"endpoint\": \"/api/v1/saas/tts\",
  \"chars_used\": 150,
  \"response_time_ms\": 1250
}
```

## 🚀 Déploiement en Production

### Docker
```bash
# Build de l'image
docker build -t tts-saas:latest .

# Run avec docker-compose
docker-compose up -d
```

### Variables d'environnement production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@db:5432/ttsdb
REDIS_URL=redis://redis:6379
STRIPE_SECRET_KEY=sk_live_...
```

### Sécurité en production
- ✅ HTTPS obligatoire
- ✅ Rate limiting activé
- ✅ Logs de sécurité
- ✅ Backup automatique
- ✅ Monitoring 24/7

## 📈 Évolutions Futures

### Roadmap technique
- [ ] **Mobile SDK** (iOS/Android)
- [ ] **Webhooks** pour les événements
- [ ] **Multi-tenancy** pour les entreprises
- [ ] **Cache intelligent** des audios
- [ ] **Analytics avancées**
- [ ] **A/B Testing** intégré

### Roadmap business
- [ ] **Programme d'affiliation**
- [ ] **White-label** pour revendeurs
- [ ] **Enterprise SSO**
- [ ] **Support multidevises**
- [ ] **Marché des voix custom**

## 🤝 Support & Contribution

### Support utilisateur
- 📧 **Email:** support@yourdomain.com
- 💬 **Chat:** Disponible dans le dashboard
- 📚 **Documentation:** /docs dans l'application

### Contribution au code
```bash
# Fork le projet
git fork https://github.com/yourusername/tts-saas

# Créer une branche
git checkout -b feature/amazing-feature

# Commit et push
git commit -m \"Add amazing feature\"
git push origin feature/amazing-feature

# Créer une Pull Request
```

## 📄 Licence

MIT License - Libre d'utilisation commerciale.

---

**🎯 Votre plateforme TTS SaaS est prête !**

Démarrez avec `python start_saas.py` et commencez à monétiser votre service de synthèse vocale dès maintenant.

Pour toute question : [Créer une issue](https://github.com/yourusername/tts-saas/issues)