#!/usr/bin/env python3
"""
Script to check which users have logged in recently
"""
from app import create_app, db
from app.models import User
from datetime import datetime, timedelta

def check_recent_logins(hours=24):
    """Check users who logged in within the last X hours"""
    app = create_app()

    with app.app_context():
        # Calculate the time threshold
        threshold = datetime.utcnow() - timedelta(hours=hours)

        # Query users who logged in recently
        recent_users = User.query.filter(User.last_login >= threshold).order_by(User.last_login.desc()).all()

        if not recent_users:
            print(f"No users have logged in within the last {hours} hours.")
            return

        print(f"Users who logged in within the last {hours} hours:")
        print("-" * 60)
        for user in recent_users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Last Login: {user.last_login}")
            print(f"Subscription: {user.subscription_status}")
            print("-" * 60)

def check_all_users():
    """Check all users and their login status"""
    app = create_app()

    with app.app_context():
        users = User.query.order_by(User.last_login.desc()).all()

        print("All users and their last login times:")
        print("-" * 60)
        for user in users:
            last_login = user.last_login if user.last_login else "Never logged in"
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Last Login: {last_login}")
            print(f"Subscription: {user.subscription_status}")
            print("-" * 60)

if __name__ == "__main__":
    print("Checking recent logins (last 24 hours):")
    check_recent_logins(24)
    print("\n" + "="*60 + "\n")
    print("All users:")
    check_all_users()