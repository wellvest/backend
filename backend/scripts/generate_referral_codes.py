#!/usr/bin/env python
"""
Script to generate referral codes for all existing users who don't have one.
Run this script from the backend directory with:
python scripts/generate_referral_codes.py
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User

def generate_referral_code(member_id):
    """Generate a referral code based on member_id."""
    return f"WV{member_id}"

def main():
    """Generate referral codes for all users who don't have one."""
    db = SessionLocal()
    try:
        # Get all users without referral codes
        users_without_codes = db.query(User).filter(User.referral_code.is_(None)).all()
        print(f"Found {len(users_without_codes)} users without referral codes")
        
        # Generate and save referral codes
        for user in users_without_codes:
            if user.member_id:
                referral_code = generate_referral_code(user.member_id)
                user.referral_code = referral_code
                print(f"Generated referral code {referral_code} for user {user.id} ({user.email})")
            else:
                print(f"Warning: User {user.id} ({user.email}) has no member_id, skipping")
        
        # Commit changes
        db.commit()
        print("Successfully updated referral codes")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
