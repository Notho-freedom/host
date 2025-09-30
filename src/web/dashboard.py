"""
Simple web dashboard for TTS SaaS users
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

from src.auth.auth_system import User, get_current_user, TierLimits

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de connexion"""
    return templates.TemplateResponse("login.html", {"request": request})

@dashboard_router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, user: User = Depends(get_current_user)):
    """Main dashboard page"""
    try:
        limits = TierLimits.get_limits(user.tier)
        usage_percentage = (user.chars_used_this_month / limits["chars_per_month"]) * 100
        
        context = {
            "request": request,
            "user": user,
            "limits": limits,
            "usage_percentage": round(usage_percentage, 2),
            "chars_remaining": limits["chars_per_month"] - user.chars_used_this_month
        }
        
        return templates.TemplateResponse("dashboard_tailwind.html", context)
    except Exception as e:
        # Rediriger vers la page de login si pas authentifié
        return RedirectResponse(url="/dashboard/login", status_code=302)


@dashboard_router.get("/api-docs", response_class=HTMLResponse) 
async def api_documentation(request: Request, user: User = Depends(get_current_user)):
    """API documentation page"""
    
    context = {
        "request": request,
        "user": user,
        "api_key": f"tts_{user.user_id[:8]}...",  # Masqué pour sécurité
        "base_url": "https://your-api-domain.com/api/v1"
    }
    
    return templates.TemplateResponse("api_docs.html", context)


@dashboard_router.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request, user: User = Depends(get_current_user)):
    """Billing and subscription management"""
    
    context = {
        "request": request,
        "user": user,
        "current_tier": user.tier.value,
        "monthly_cost": {
            "free": 0,
            "starter": 10, 
            "pro": 49,
            "enterprise": 199
        }.get(user.tier.value, 0)
    }
    
    return templates.TemplateResponse("billing.html", context)