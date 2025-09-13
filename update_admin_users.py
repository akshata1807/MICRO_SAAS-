#!/usr/bin/env python3
"""
Update existing AdminUser records to add subscription_status
"""
from app import create_app, db
from app.models import AdminUser

def update_admin_users():
    """Update existing admin users with subscription status"""
    app = create_app()
    
    with app.app_context():
        # Update all existing admin users to have premium status
        admin_users = AdminUser.query.all()
        for admin in admin_users:
            if not hasattr(admin, 'subscription_status') or admin.subscription_status is None:
                admin.subscription_status = 'premium'
                print(f"Updated admin {admin.username} with premium subscription status")
        
        db.session.commit()
        print(f"✅ Updated {len(admin_users)} admin users with subscription status")

if __name__ == "__main__":
    update_admin_users()
