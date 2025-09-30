"""
SaaS API routes with authentication, billing, and usage tracking
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

# Import existing TTS functionality
from src.models.schemas import TTSRequest
from src.services.tts_service import tts_service
from src.auth.auth_system import (
    User, UserTier, AuthService, 
    get_current_user, check_rate_limits, check_text_length_limit,
    track_usage, TierLimits
)

# Créer l'instance du service d'authentification
auth_service = AuthService()

logger = logging.getLogger(__name__)

# Routers
auth_router = APIRouter(tags=["authentication"])
saas_router = APIRouter(tags=["saas-tts"])
billing_router = APIRouter(tags=["billing"])


# === AUTHENTICATION ROUTES ===

class UserRegistration(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str = "User"
    tier: UserTier = UserTier.FREE


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user: Dict[str, Any]


@auth_router.post("/register", response_model=Token)
async def register_user(user_data: UserRegistration):
    """Register new user account"""
    try:
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            tier=user_data.tier
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_service.create_access_token(
            data={"sub": user.user_id}, expires_delta=access_token_expires
        )
        
        logger.info(f"New user registered: {user.email} ({user.tier})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@auth_router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Authenticate user and return token"""
    user = await auth_service.authenticate_user(
        email=user_data.email,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@auth_router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    limits = TierLimits.get_limits(current_user.tier)
    
    return {
        "user": current_user.to_dict(),
        "tier_limits": limits,
        "usage_percentage": (current_user.chars_used_this_month / limits["chars_per_month"]) * 100
    }


# === SAAS TTS ROUTES ===

class SaaSTTSRequest(TTSRequest):
    """Enhanced TTS request with SaaS features"""
    webhook_url: Optional[str] = None
    priority: bool = False  # Premium feature


class UsageResponse(BaseModel):
    """Usage tracking response"""
    chars_processed: int
    chars_remaining: int
    tier: str
    upgrade_recommended: bool = False


@saas_router.post("/tts", dependencies=[Depends(check_rate_limits)])
async def generate_tts_saas(
    request: SaaSTTSRequest,
    current_user: User = Depends(check_text_length_limit)
):
    """Generate TTS audio with SaaS features and usage tracking"""
    
    try:
        # Check monthly quota
        chars_to_use = len(request.text)
        limits = TierLimits.get_limits(current_user.tier)
        
        if (current_user.chars_used_this_month + chars_to_use) > limits["chars_per_month"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Monthly quota exceeded. Please upgrade your plan."
            )
        
        # Log TTS request
        logger.info(
            f"TTS request: user={current_user.user_id} tier={current_user.tier} "
            f"chars={chars_to_use} voice={request.voice}"
        )
        
        # Generate audio using existing service
        audio_data = await tts_service.generate_audio(
            text=request.text, 
            voice=request.voice
        )
        
        # Track usage
        await track_usage(current_user.user_id, chars_to_use)
        
        # Prepare response headers with usage info
        chars_remaining = limits["chars_per_month"] - (current_user.chars_used_this_month + chars_to_use)
        
        headers = {
            "X-Chars-Used": str(chars_to_use),
            "X-Chars-Remaining": str(chars_remaining),
            "X-Tier": current_user.tier.value,
            "X-Rate-Limit": str(limits["requests_per_minute"])
        }
        
        # Send webhook if provided (premium feature)
        if request.webhook_url and current_user.tier != UserTier.FREE:
            # TODO: Implement webhook notification
            pass
        
        return StreamingResponse(
            audio_data,
            media_type="audio/mpeg",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation error for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TTS generation failed"
        )


@saas_router.get("/voices", dependencies=[Depends(check_rate_limits)])
async def get_available_voices(current_user: User = Depends(get_current_user)):
    """Get available voices based on user tier"""
    
    try:
        # Get all voices
        all_voices = await tts_service.get_all_voices()
        
        # Filter based on tier limits
        limits = TierLimits.get_limits(current_user.tier)
        max_voices = limits["voices_available"]
        
        # Return subset based on tier (premium voices for paid tiers)
        if current_user.tier == UserTier.FREE:
            # Free tier gets basic voices only
            filtered_voices = [v for v in all_voices if "Neural" in v.get("Name", "")][:max_voices]
        else:
            # Paid tiers get more voices
            filtered_voices = all_voices[:max_voices]
        
        return {
            "voices": filtered_voices,
            "count": len(filtered_voices),
            "tier": current_user.tier.value,
            "max_voices": max_voices
        }
        
    except Exception as e:
        logger.error(f"Error fetching voices for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch voices"
        )


@saas_router.get("/usage")
async def get_usage_stats(current_user: User = Depends(get_current_user)):
    """Get current user usage statistics"""
    
    limits = TierLimits.get_limits(current_user.tier)
    usage_percentage = (current_user.chars_used_this_month / limits["chars_per_month"]) * 100
    
    return {
        "user_id": current_user.user_id,
        "tier": current_user.tier.value,
        "current_month": {
            "chars_used": current_user.chars_used_this_month,
            "chars_limit": limits["chars_per_month"],
            "usage_percentage": round(usage_percentage, 2)
        },
        "rate_limits": {
            "requests_per_minute": limits["requests_per_minute"],
            "max_text_length": limits["max_text_length"]
        },
        "upgrade_recommended": usage_percentage > 80,
        "next_tier": "starter" if current_user.tier == UserTier.FREE else "pro"
    }


# === BILLING ROUTES ===

class UpgradeRequest(BaseModel):
    """Tier upgrade request"""
    new_tier: UserTier
    payment_method: str = "stripe"


@billing_router.post("/upgrade")
async def upgrade_tier(
    upgrade_data: UpgradeRequest,
    current_user: User = Depends(get_current_user)
):
    """Upgrade user to higher tier"""
    
    if upgrade_data.new_tier == current_user.tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this tier"
        )
    
    # TODO: Implement Stripe payment processing
    
    # For now, simulate successful upgrade
    logger.info(f"User {current_user.user_id} upgraded from {current_user.tier} to {upgrade_data.new_tier}")
    
    return {
        "success": True,
        "old_tier": current_user.tier.value,
        "new_tier": upgrade_data.new_tier.value,
        "message": "Tier upgraded successfully",
        "new_limits": TierLimits.get_limits(upgrade_data.new_tier)
    }


@billing_router.get("/pricing")
async def get_pricing():
    """Get current pricing tiers"""
    
    return {
        "tiers": {
            "free": {
                "price": 0,
                "currency": "EUR",
                "limits": TierLimits.get_limits(UserTier.FREE),
                "features": ["Basic API", "5 voices", "Community support"]
            },
            "starter": {
                "price": 10,
                "currency": "EUR",
                "billing": "monthly",
                "limits": TierLimits.get_limits(UserTier.STARTER),
                "features": ["20 voices", "Email support", "Higher rate limits"]
            },
            "pro": {
                "price": 49,
                "currency": "EUR", 
                "billing": "monthly",
                "limits": TierLimits.get_limits(UserTier.PRO),
                "features": ["50+ voices", "SSML support", "Priority support", "Webhooks"]
            },
            "enterprise": {
                "price": 199,
                "currency": "EUR",
                "billing": "monthly", 
                "limits": TierLimits.get_limits(UserTier.ENTERPRISE),
                "features": ["All voices", "Custom voices", "24/7 support", "SLA", "On-premise"]
            }
        }
    }


# === ADMIN ROUTES ===

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# TODO: Add admin authentication middleware

@admin_router.get("/stats")
async def get_admin_stats():
    """Get overall service statistics (admin only)"""
    
    # TODO: Implement admin authentication
    # TODO: Get real stats from database
    
    return {
        "total_users": 1250,
        "active_users_today": 890,
        "total_characters_processed": 15000000,
        "revenue_this_month": 12500,
        "top_tiers": {
            "free": 850,
            "starter": 250,
            "pro": 120,
            "enterprise": 30
        }
    }