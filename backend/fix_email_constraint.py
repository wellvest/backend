#!/usr/bin/env python3
"""
Script to make email optional in the database schema
"""
import sys
from sqlalchemy import text
from app.db.database import engine

def update_schema():
    """Update the database schema to make email optional"""
    try:
        with engine.connect() as conn:
            # Make email nullable
            conn.execute(text("ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"))
            conn.commit()
            print("Database schema updated successfully! Email is now optional.")
            return True
    except Exception as e:
        print(f"Error updating database schema: {e}")
        return False

if __name__ == "__main__":
    success = update_schema()
    if not success:
        sys.exit(1)
