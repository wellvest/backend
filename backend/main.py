from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.routes import auth, users, profile, investments, wallets, network, uploads, referrals, contact, plans, noc, bonus, auth_reset_password, notifications, otp, payments
from app.core.config import settings
from app.db.database import engine
from app.admin import setup_admin
from app.admin.payment_routes import router as admin_payment_router

app = FastAPI(
    title="WellVest API",
    description="Backend API for WellVest application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Add all your frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Setup admin interface
admin = setup_admin(app, engine)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(investments.router, prefix="/api", tags=["Investments"])
app.include_router(wallets.router, prefix="/api", tags=["Wallets"])
app.include_router(network.router, prefix="/api", tags=["Network"])
app.include_router(uploads.router, prefix="/api", tags=["Uploads"])
app.include_router(referrals.router, prefix="/api", tags=["Referrals"])
app.include_router(contact.router, prefix="/api", tags=["Contact"])
app.include_router(plans.router, prefix="/api", tags=["Plans"])
app.include_router(noc.router, prefix="/api", tags=["NOC"])
app.include_router(bonus.router, prefix="/api", tags=["Bonus"])
app.include_router(auth_reset_password.router, prefix="/api", tags=["Authentication"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(otp.router, prefix="/api", tags=["Authentication"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# Include admin payment routes
app.include_router(admin_payment_router, tags=["Admin"])

# Mount static files for uploads
# Using the same UPLOAD_DIR as defined in uploads.py
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

# Ensure proper permissions on upload directories
import subprocess
subprocess.run(["chmod", "-R", "755", UPLOAD_DIR])

# Mount uploads directory with explicit HTML disabled for security
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR, html=False), name="uploads")

# Mount frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "WellVest API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
