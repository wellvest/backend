from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import create_access_token
from app.core.config import settings
import secrets
from datetime import timedelta

class AdminAuth(AuthenticationBackend):
    """Authentication backend for the admin interface"""
    
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # Check if the credentials match the admin credentials
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            # Generate a random token for the session
            token = secrets.token_hex(16)
            request.session.update({"token": token, "username": username})
            return True
        
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        username = request.session.get("username")
        
        if not token or not username:
            return False
        
        # Check if the username is the admin username
        if username == settings.ADMIN_USERNAME:
            return True
        
        return False

def get_admin_auth_backend() -> AdminAuth:
    """Get the admin authentication backend"""
    return AdminAuth(secret_key=settings.SECRET_KEY)
