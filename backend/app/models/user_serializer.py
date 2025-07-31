"""
Serializer functions for user models to ensure proper URL handling
"""
from app.models.user import User
from app.utils.url_utils import ensure_relative_url

def serialize_user(user: User) -> dict:
    """
    Serialize a User model instance to a dictionary with proper URL handling.
    
    Args:
        user: The User model instance to serialize
        
    Returns:
        A dictionary representation of the user with properly formatted URLs
    """
    user_dict = {
        "id": user.id,
        "member_id": user.member_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "gender": user.gender,
        "join_date": user.join_date,
        "is_active": user.is_active,
        "referral_code": user.referral_code,
    }
    
    # Ensure avatar URL is relative
    if user.avatar:
        user_dict["avatar"] = ensure_relative_url(user.avatar)
    else:
        user_dict["avatar"] = None
        
    return user_dict
