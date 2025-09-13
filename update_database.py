#!/usr/bin/env python3
"""
Script to update the database with new models.
Run this script to add the new Resume, Certificate, and AdminUser tables.
"""

from app import create_app, db
from app.models import User, Invoice, QRCode, Resume, Certificate, Subscription, AdminUser

def update_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database updated successfully!")
            print("New tables created:")
            print("- Resume")
            print("- Certificate") 
            print("- AdminUser")
            print("\nYou can now run the application with the new admin panel.")
        except Exception as e:
            print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    update_database()
