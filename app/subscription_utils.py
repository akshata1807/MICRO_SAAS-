"""
Subscription and feature restriction utilities
"""
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def has_subscription(required_plan='basic'):
    """
    Check if user has required subscription level
    Plans: free < basic < pro < premium
    """
    if not current_user.is_authenticated:
        return False
    
    # Admin users always have premium access
    if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
        return True
    
    plan_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'premium': 3}
    subscription_status = getattr(current_user, 'subscription_status', 'free')
    user_plan_level = plan_hierarchy.get(subscription_status, 0)
    required_plan_level = plan_hierarchy.get(required_plan, 1)
    
    return user_plan_level >= required_plan_level

def subscription_required(plan='basic'):
    """
    Decorator to require subscription for access
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_subscription(plan):
                flash(f'This feature requires a {plan.title()} subscription. Please upgrade your plan.', 'warning')
                return redirect(url_for('billing.subscribe'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_limits():
    """
    Get user's current limits based on subscription
    """
    limits = {
        'free': {
            'invoices_per_month': 5,
            'resumes_per_month': 3,
            'certificates_per_month': 2,
            'qrcodes_per_month': 10,
            'templates': ['basic'],
            'bulk_operations': False,
            'premium_templates': False
        },
        'basic': {
            'invoices_per_month': 50,
            'resumes_per_month': 25,
            'certificates_per_month': 20,
            'qrcodes_per_month': 100,
            'templates': ['basic', 'professional'],
            'bulk_operations': False,
            'premium_templates': False
        },
        'pro': {
            'invoices_per_month': 200,
            'resumes_per_month': 100,
            'certificates_per_month': 100,
            'qrcodes_per_month': 500,
            'templates': ['basic', 'professional', 'modern'],
            'bulk_operations': True,
            'premium_templates': True
        },
        'premium': {
            'invoices_per_month': -1,  # unlimited
            'resumes_per_month': -1,
            'certificates_per_month': -1,
            'qrcodes_per_month': -1,
            'templates': ['basic', 'professional', 'modern', 'executive'],
            'bulk_operations': True,
            'premium_templates': True
        }
    }
    
    # Handle admin users - they get premium access
    if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
        return limits['premium']
    
    # Get subscription status, default to 'free' if not available
    subscription_status = getattr(current_user, 'subscription_status', 'free')
    return limits.get(subscription_status, limits['free'])

def check_usage_limit(file_type):
    """
    Check if user has reached their usage limit for a file type
    """
    if not current_user.is_authenticated:
        return False, "Please log in to use this feature"
    
    # Admin users have unlimited access
    if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
        return True, "Unlimited usage (Admin access)"
    
    limits = get_user_limits()
    limit_key = f"{file_type}s_per_month"
    monthly_limit = limits.get(limit_key, 0)
    
    if monthly_limit == -1:  # unlimited
        return True, "Unlimited usage"
    
    # Count current month's usage
    from datetime import datetime
    from app.models import Invoice, Resume, Certificate, QRCode
    
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if file_type == 'invoice':
        count = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            Invoice.created_at >= current_month
        ).count()
    elif file_type == 'resume':
        count = Resume.query.filter(
            Resume.user_id == current_user.id,
            Resume.created_at >= current_month
        ).count()
    elif file_type == 'certificate':
        count = Certificate.query.filter(
            Certificate.user_id == current_user.id,
            Certificate.created_at >= current_month
        ).count()
    elif file_type == 'qrcode':
        count = QRCode.query.filter(
            QRCode.user_id == current_user.id,
            QRCode.created_at >= current_month
        ).count()
    else:
        return False, "Invalid file type"
    
    if count >= monthly_limit:
        return False, f"You have reached your monthly limit of {monthly_limit} {file_type}s. Please upgrade your plan for more."
    
    return True, f"{monthly_limit - count} {file_type}s remaining this month"

def can_use_premium_template():
    """
    Check if user can use premium templates
    """
    # Admin users always have premium access
    if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
        return True
    
    limits = get_user_limits()
    return limits.get('premium_templates', False)

def can_use_bulk_operations():
    """
    Check if user can use bulk operations
    """
    # Admin users always have bulk operations access
    if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
        return True
    
    limits = get_user_limits()
    return limits.get('bulk_operations', False)
