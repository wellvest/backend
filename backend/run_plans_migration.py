"""
Script to run the plans table migration
"""
from app.db.migrations.add_plans_table import create_plans_table

if __name__ == "__main__":
    print("Running migration to create plans table...")
    create_plans_table()
    print("Migration completed successfully.")
