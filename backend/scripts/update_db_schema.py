#!/usr/bin/env python3
"""
Script to update the database schema to make email optional and phone required
"""
import os
import sys

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def run_sql_script(file_path):
    """Run a SQL script file"""
    with open(file_path, 'r') as f:
        sql_script = f.read()
    
    with engine.connect() as conn:
        conn.execute(text(sql_script))
        conn.commit()
        print(f"Successfully executed SQL script: {file_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, "alter_user_table.sql")
    
    try:
        run_sql_script(sql_file)
        print("Database schema updated successfully!")
    except Exception as e:
        print(f"Error updating database schema: {e}")
        sys.exit(1)
