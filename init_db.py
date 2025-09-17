#!/usr/bin/env python3
"""
Initialize the database for the fitness app
"""
from app import app, db
from models import init_db

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        print("🗄️  Creating database tables...")
        init_db()
        print("✅ Database initialized successfully!")
        print("📁 Database file: fitness.db")

if __name__ == '__main__':
    init_database()