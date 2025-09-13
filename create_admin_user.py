#!/usr/bin/env python3
"""
Script to create the first admin user for the MicroSaaS application.
Run this script to set up the initial admin account.
"""

from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if any admin users exist
        existing_admin = AdminUser.query.first()
        if existing_admin:
            print("Admin user already exists!")
            print(f"Existing admin: {existing_admin.username} ({existing_admin.email})")
            return
        
        # Create the first super admin
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not username or not email or not password:
            print("All fields are required!")
            return
        
        # Check if email already exists
        if AdminUser.query.filter_by(email=email).first():
            print("Admin with this email already exists!")
            return
        
        # Create admin user
        hashed_password = generate_password_hash(password)
        admin = AdminUser(
            username=username,
            email=email,
            password=hashed_password,
            is_super_admin=True
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin user '{username}' created successfully!")
            print(f"Email: {email}")
            print(f"Super Admin: Yes")
            print("\nYou can now login to the admin panel at: /admin/login")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()
