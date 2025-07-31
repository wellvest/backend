from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Response
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import io
from typing import Optional
from PIL import Image, ImageDraw

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

@router.post("/uploads/avatar", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload user avatar image."""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Update user avatar URL
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_user.avatar = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"avatar_url": avatar_url}


@router.get("/placeholder/{width}/{height}")
async def get_placeholder_image(width: int, height: int):
    """
    Generate a placeholder image with specified dimensions.
    Used for UI elements that need a placeholder before actual images are loaded.
    """
    try:
        # Validate dimensions to prevent excessive resource usage
        if width > 1000 or height > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image dimensions too large. Maximum allowed is 1000x1000"
            )
            
        # Create a gray placeholder image with the specified dimensions
        img = Image.new('RGB', (width, height), color=(200, 200, 200))
        
        # Add a simple pattern or text to indicate it's a placeholder
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [(0, 0), (width, height)],
            outline=(180, 180, 180),
            width=2
        )
        
        # Draw diagonal line
        draw.line([(0, 0), (width, height)], fill=(180, 180, 180), width=1)
        draw.line([(0, height), (width, 0)], fill=(180, 180, 180), width=1)
        
        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return Response(
            content=img_byte_arr.getvalue(),
            media_type="image/png"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating placeholder image: {str(e)}"
        )
