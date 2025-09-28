#!/usr/bin/env python3
"""
Database migration script to add missing columns to user and admin_user tables
"""
from app import create_app, db
from sqlalchemy import text
from datetime import datetime

def migrate_database():
    """Add missing columns to user and admin_user tables"""
    app = create_app()

    with app.app_context():
        try:
            # Add created_at column to user table
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN created_at DATETIME"))
                    conn.commit()
                print("Added created_at column to user table")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print("Column created_at already exists in user table")
                else:
                    print(f"Error adding created_at to user table: {e}")

            # Add last_login column to user table
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN last_login DATETIME"))
                    conn.commit()
                print("Added last_login column to user table")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print("Column last_login already exists in user table")
                else:
                    print(f"Error adding last_login to user table: {e}")

            # Add subscription_status column to admin_user table
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE admin_user ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'premium'"))
                    conn.commit()
                print("Added subscription_status column to admin_user table")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print("Column subscription_status already exists in admin_user table")
                else:
                    print(f"Error adding subscription_status to admin_user table: {e}")

            # Add created_at column to admin_user table
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE admin_user ADD COLUMN created_at DATETIME"))
                    conn.commit()
                print("Added created_at column to admin_user table")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print("Column created_at already exists in admin_user table")
                else:
                    print(f"Error adding created_at to admin_user table: {e}")

            # Update existing records with current timestamp
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                    conn.commit()
                print("Updated existing user records with created_at timestamp")
            except Exception as e:
                print(f"Warning updating user created_at: {e}")

            try:
                with db.engine.connect() as conn:
                    conn.execute(text("UPDATE admin_user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                    conn.commit()
                print("Updated existing admin_user records with created_at timestamp")
            except Exception as e:
                print(f"Warning updating admin_user created_at: {e}")

        except Exception as e:
            print(f"Error during migration: {e}")
            return False

        print("Database migration completed successfully!")
        return True

if __name__ == "__main__":
    migrate_database()
