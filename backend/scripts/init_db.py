import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.core.config import settings
from app.db.init_db import init_db

def main() -> None:
    """Initialize the database with tables and demo data."""
    print("Creating database tables...")
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    print("Initializing demo data...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    
    print("Database initialization completed successfully!")

if __name__ == "__main__":
    main()
