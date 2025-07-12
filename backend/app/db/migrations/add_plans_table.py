"""
Migration script to add plans table to the database
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost/wellvest"

# Create engine and base
engine = create_engine(DATABASE_URL)
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Define Plan model
class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)
    returns_percentage = Column(Float, default=15.0)
    duration_months = Column(Integer, default=12)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

def create_plans_table():
    # Create the plans table
    Base.metadata.create_all(engine)
    
    # Create initial plans
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if plans already exist
    existing_plans = session.query(Plan).all()
    if existing_plans:
        print("Plans already exist, skipping creation.")
        return
    
    # Create default plans
    plans = [
        Plan(
            name="Basic Plan",
            min_amount=10000.0,
            max_amount=50000.0,
            returns_percentage=15.0,
            duration_months=12
        ),
        Plan(
            name="Standard Plan",
            min_amount=50000.0,
            max_amount=100000.0,
            returns_percentage=15.0,
            duration_months=12
        ),
        Plan(
            name="Premium Plan",
            min_amount=100000.0,
            max_amount=500000.0,
            returns_percentage=15.0,
            duration_months=12
        ),
        Plan(
            name="Gold Plan",
            min_amount=500000.0,
            max_amount=1000000.0,
            returns_percentage=15.0,
            duration_months=12
        ),
        Plan(
            name="Platinum Plan",
            min_amount=1000000.0,
            max_amount=5000000.0,
            returns_percentage=15.0,
            duration_months=12
        )
    ]
    
    for plan in plans:
        session.add(plan)
    
    session.commit()
    print("Created plans table and added default plans.")

if __name__ == "__main__":
    create_plans_table()
