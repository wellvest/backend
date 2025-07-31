"""
Script to update the database schema to make email optional and phone required
"""
from sqlalchemy import text
from app.db.database import engine

def update_schema():
    """Update the database schema to make email optional and phone required"""
    with engine.connect() as conn:
        # Make email nullable
        conn.execute(text("ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"))
        # Make phone not nullable and add unique constraint
        conn.execute(text("ALTER TABLE users ALTER COLUMN phone SET NOT NULL;"))
        conn.execute(text("ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);"))
        # Add index to phone for faster lookups if it doesn't exist
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_phone ON users (phone);"))
        conn.commit()
        print("Database schema updated successfully!")

if __name__ == "__main__":
    update_schema()
