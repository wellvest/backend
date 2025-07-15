from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.auth import get_current_active_user
from app.utils.notification_utils import send_bonus_credited_notification

router = APIRouter()

@router.get("/", response_model=List)
def get_bonuses(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get all bonuses for the current user
    """
    # Placeholder for actual implementation
    return []
