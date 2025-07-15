from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            message=notification_data.message,
            type=notification_data.type,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get all notifications for a user."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).count()

    def mark_as_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.read = True
            self.db.commit()
            self.db.refresh(notification)
        
        return notification

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read."""
        result = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).update({"read": True})
        
        self.db.commit()
        return result

    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def create_system_notification(
        self, 
        user_id: str, 
        title: str, 
        message: str, 
        notification_type: str = "info"
    ) -> Notification:
        """Helper method to quickly create a system notification."""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type
        )
        return self.create_notification(notification_data)
        
    @staticmethod
    def create_payment_notification(db: Session, user_id: str, payment_id: str, amount: float) -> None:
        """Create a notification for a new payment submission."""
        from app.utils.notification_utils import send_payment_notification
        send_payment_notification(db, user_id, payment_id, amount)
    
    @staticmethod
    def create_payment_approved_notification(db: Session, user_id: str, payment_id: str, amount: float) -> None:
        """Create a notification for an approved payment."""
        from app.utils.notification_utils import send_payment_approved_notification
        send_payment_approved_notification(db, user_id, payment_id, amount)
    
    @staticmethod
    def create_payment_rejected_notification(db: Session, user_id: str, payment_id: str, amount: float, reason: str) -> None:
        """Create a notification for a rejected payment."""
        from app.utils.notification_utils import send_payment_rejected_notification
        send_payment_rejected_notification(db, user_id, payment_id, amount, reason)
        
    @staticmethod
    def create_team_investment_notification(db: Session, user_id: str, amount: float, level: int, team_member_name: str) -> None:
        """Create a notification for a team investment commission."""
        from app.utils.notification_utils import send_team_investment_notification
        send_team_investment_notification(db, user_id, amount, level, team_member_name)
