"""
Authentication and Authorization system for TTS SaaS
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis
from enum import Enum

# Configuration
SECRET_KEY = "your-secret-key-here"  # À changer en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REDIS_URL = "redis://localhost:6379"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
redis_client = redis.from_url(REDIS_URL)


class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TierLimits:
    """Rate limits and quotas per tier"""
    
    LIMITS = {
        UserTier.FREE: {
            "chars_per_month": 1000,
            "requests_per_minute": 5,
            "max_text_length": 500,
            "voices_available": 5
        },
        UserTier.STARTER: {
            "chars_per_month": 50000,
            "requests_per_minute": 20,
            "max_text_length": 2000,
            "voices_available": 20
        },
        UserTier.PRO: {
            "chars_per_month": 500000,
            "requests_per_minute": 100,
            "max_text_length": 10000,
            "voices_available": 50
        },
        UserTier.ENTERPRISE: {
            "chars_per_month": 5000000,
            "requests_per_minute": 500,
            "max_text_length": 50000,
            "voices_available": 100
        }
    }
    
    @classmethod
    def get_limits(cls, tier: UserTier) -> Dict[str, Any]:
        return cls.LIMITS.get(tier, cls.LIMITS[UserTier.FREE])


class User:
    """User model"""
    
    def __init__(self, user_id: str, email: str, tier: UserTier, 
                 chars_used_this_month: int = 0, created_at: datetime = None):
        self.user_id = user_id
        self.email = email
        self.tier = tier
        self.chars_used_this_month = chars_used_this_month
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "tier": self.tier.value,
            "chars_used_this_month": self.chars_used_this_month,
            "created_at": self.created_at.isoformat()
        }


class AuthService:
    """Authentication and user management service"""
    
    def __init__(self):
        self.users_db = {}  # En production: vraie base de données
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email/password"""
        # En production: requête base de données
        user_data = self.users_db.get(email)
        if not user_data:
            return None
        
        if not self.verify_password(password, user_data["hashed_password"]):
            return None
            
        return User(
            user_id=user_data["user_id"],
            email=email,
            tier=UserTier(user_data["tier"]),
            chars_used_this_month=user_data.get("chars_used_this_month", 0)
        )
    
    async def create_user(self, email: str, password: str, tier: UserTier = UserTier.FREE) -> User:
        """Create new user account"""
        import uuid
        
        if email in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        user_data = {
            "user_id": user_id,
            "hashed_password": hashed_password,
            "tier": tier.value,
            "chars_used_this_month": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.users_db[email] = user_data
        
        return User(user_id=user_id, email=email, tier=tier)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for email, user_data in self.users_db.items():
            if user_data["user_id"] == user_id:
                return User(
                    user_id=user_id,
                    email=email,
                    tier=UserTier(user_data["tier"]),
                    chars_used_this_month=user_data.get("chars_used_this_month", 0)
                )
        return None


class RateLimiter:
    """Rate limiting service"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_rate_limited(self, user_id: str, tier: UserTier) -> bool:
        """Check if user is rate limited"""
        limits = TierLimits.get_limits(tier)
        rpm_limit = limits["requests_per_minute"]
        
        key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d-%H-%M')}"
        
        try:
            current_count = self.redis.incr(key)
            if current_count == 1:
                self.redis.expire(key, 60)  # Expire après 1 minute
            
            return current_count > rpm_limit
        except:
            # Si Redis n'est pas disponible, on laisse passer
            return False
    
    async def check_monthly_quota(self, user_id: str, tier: UserTier, chars_to_use: int) -> bool:
        """Check if user has exceeded monthly quota"""
        # En production: récupérer depuis la base de données
        limits = TierLimits.get_limits(tier)
        monthly_limit = limits["chars_per_month"]
        
        # Simuler récupération usage actuel
        current_usage = 0  # À récupérer depuis DB
        
        return (current_usage + chars_to_use) <= monthly_limit


# Services globaux
auth_service = AuthService()
rate_limiter = RateLimiter(redis_client)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def check_rate_limits(user: User = Depends(get_current_user)):
    """Dependency to check rate limits"""
    if await rate_limiter.is_rate_limited(user.user_id, user.tier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please upgrade your plan."
        )
    return user


async def check_text_length_limit(text: str, user: User = Depends(get_current_user)):
    """Check text length against user tier limits"""
    limits = TierLimits.get_limits(user.tier)
    max_length = limits["max_text_length"]
    
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text too long. Maximum {max_length} characters for {user.tier} tier."
        )
    
    return user


# Usage tracking
async def track_usage(user_id: str, chars_used: int):
    """Track character usage for billing"""
    # En production: mettre à jour dans la base de données
    key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
    try:
        redis_client.incr(key, chars_used)
        redis_client.expire(key, 86400 * 32)  # Expire après 32 jours
    except:
        pass  # Log error en production