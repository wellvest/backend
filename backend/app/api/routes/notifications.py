from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all notifications for the current user.
    """
    notification_service = NotificationService(db)
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return notifications


@router.get("/unread-count", response_model=int)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications for the current user.
    """
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(user_id=current_user.id)
    return count


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read.
    """
    notification_service = NotificationService(db)
    notification = notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.patch("/mark-all-read", response_model=int)
@router.post("/mark-all-read", response_model=int)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user.
    Returns the number of notifications updated.
    """
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(user_id=current_user.id)
    return count


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification.
    """
    notification_service = NotificationService(db)
    success = notification_service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
