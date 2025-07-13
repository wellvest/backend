#!/usr/bin/env python3
"""
Script to update the database schema to make email optional and phone required
"""
import sys
from sqlalchemy import text
from app.db.database import engine

def update_schema():
    """Update the database schema to make email optional and phone required"""
    try:
        with engine.connect() as conn:
            # Make email nullable
            conn.execute(text("ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"))
            # Make phone not nullable and add unique constraint if not exists
            conn.execute(text("ALTER TABLE users ALTER COLUMN phone SET NOT NULL;"))
            
            # Check if constraint exists before adding
            result = conn.execute(text(
                "SELECT constraint_name FROM information_schema.table_constraints "
                "WHERE table_name = 'users' AND constraint_name = 'users_phone_key'"
            ))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);"))
            
            # Add index to phone for faster lookups if it doesn't exist
            conn.execute(text(
                "SELECT 1 FROM pg_indexes WHERE tablename = 'users' AND indexname = 'ix_users_phone'"
            ))
            if not result.fetchone():
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_phone ON users (phone);"))
            
            conn.commit()
            print("Database schema updated successfully!")
            return True
    except Exception as e:
        print(f"Error updating database schema: {e}")
        return False

if __name__ == "__main__":
    success = update_schema()
    if not success:
        sys.exit(1)
