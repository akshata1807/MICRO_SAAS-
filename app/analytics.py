"""
Advanced analytics and reporting system
"""
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Invoice, Resume, Certificate, QRCode, Subscription, db
from app.subscription_utils import has_subscription
from datetime import datetime, timedelta
from sqlalchemy import func, desc, extract
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Main analytics dashboard"""
    if not has_subscription('pro'):
        flash('Analytics dashboard requires a Pro or Premium subscription.', 'warning')
        return redirect(url_for('billing.subscribe'))
    
    # Get date range (default to last 30 days)
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User activity data
    user_stats = get_user_activity_stats(start_date, end_date)
    file_stats = get_file_generation_stats(start_date, end_date)
    subscription_stats = get_subscription_stats()
    daily_activity = get_daily_activity_data(start_date, end_date)
    
    return render_template('analytics/dashboard.html',
                         user_stats=user_stats,
                         file_stats=file_stats,
                         subscription_stats=subscription_stats,
                         daily_activity=daily_activity,
                         days=days)

@analytics_bp.route('/analytics/api/daily-activity')
@login_required
def daily_activity_api():
    """API endpoint for daily activity data"""
    if not has_subscription('pro'):
        return jsonify({'error': 'Pro subscription required'}), 403
    
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    data = get_daily_activity_data(start_date, end_date)
    return jsonify(data)

@analytics_bp.route('/analytics/api/user-growth')
@login_required
def user_growth_api():
    """API endpoint for user growth data"""
    if not has_subscription('pro'):
        return jsonify({'error': 'Pro subscription required'}), 403
    
    days = int(request.args.get('days', 90))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    data = get_user_growth_data(start_date, end_date)
    return jsonify(data)

@analytics_bp.route('/analytics/api/revenue')
@login_required
def revenue_api():
    """API endpoint for revenue data"""
    if not has_subscription('premium'):
        return jsonify({'error': 'Premium subscription required'}), 403
    
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    data = get_revenue_data(start_date, end_date)
    return jsonify(data)

def get_user_activity_stats(start_date, end_date):
    """Get user activity statistics"""
    total_users = User.query.count()
    active_users = User.query.filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).count()
    
    verified_users = User.query.filter_by(is_verified=True).count()
    premium_users = User.query.filter(
        User.subscription_status.in_(['pro', 'premium'])
    ).count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'premium_users': premium_users,
        'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 2),
        'premium_rate': round((premium_users / total_users * 100) if total_users > 0 else 0, 2)
    }

def get_file_generation_stats(start_date, end_date):
    """Get file generation statistics"""
    invoices = Invoice.query.filter(
        Invoice.created_at >= start_date,
        Invoice.created_at <= end_date
    ).count()
    
    resumes = Resume.query.filter(
        Resume.created_at >= start_date,
        Resume.created_at <= end_date
    ).count()
    
    certificates = Certificate.query.filter(
        Certificate.created_at >= start_date,
        Certificate.created_at <= end_date
    ).count()
    
    qrcodes = QRCode.query.filter(
        QRCode.created_at >= start_date,
        QRCode.created_at <= end_date
    ).count()
    
    total_files = invoices + resumes + certificates + qrcodes
    
    return {
        'invoices': invoices,
        'resumes': resumes,
        'certificates': certificates,
        'qrcodes': qrcodes,
        'total_files': total_files,
        'avg_files_per_day': round(total_files / ((end_date - start_date).days + 1), 2)
    }

def get_subscription_stats():
    """Get subscription statistics"""
    total_subscriptions = Subscription.query.count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    
    # Plan distribution
    basic_count = Subscription.query.filter_by(plan='basic', status='active').count()
    pro_count = Subscription.query.filter_by(plan='pro', status='active').count()
    premium_count = Subscription.query.filter_by(plan='premium', status='active').count()
    
    return {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'basic_count': basic_count,
        'pro_count': pro_count,
        'premium_count': premium_count,
        'conversion_rate': round((active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0, 2)
    }

def get_daily_activity_data(start_date, end_date):
    """Get daily activity data for charts"""
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Count files created on this day
        day_invoices = Invoice.query.filter(
            Invoice.created_at >= current_date,
            Invoice.created_at < next_date
        ).count()
        
        day_resumes = Resume.query.filter(
            Resume.created_at >= current_date,
            Resume.created_at < next_date
        ).count()
        
        day_certificates = Certificate.query.filter(
            Certificate.created_at >= current_date,
            Certificate.created_at < next_date
        ).count()
        
        day_qrcodes = QRCode.query.filter(
            QRCode.created_at >= current_date,
            QRCode.created_at < next_date
        ).count()
        
        # Count new users
        day_users = User.query.filter(
            User.created_at >= current_date,
            User.created_at < next_date
        ).count()
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'invoices': day_invoices,
            'resumes': day_resumes,
            'certificates': day_certificates,
            'qrcodes': day_qrcodes,
            'total_files': day_invoices + day_resumes + day_certificates + day_qrcodes,
            'new_users': day_users
        })
        
        current_date = next_date
    
    return daily_data

def get_user_growth_data(start_date, end_date):
    """Get user growth data for charts"""
    growth_data = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Cumulative user count up to this date
        total_users = User.query.filter(User.created_at < next_date).count()
        new_users = User.query.filter(
            User.created_at >= current_date,
            User.created_at < next_date
        ).count()
        
        growth_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total_users': total_users,
            'new_users': new_users
        })
        
        current_date = next_date
    
    return growth_data

def get_revenue_data(start_date, end_date):
    """Get revenue data (mock data for demo)"""
    # This would integrate with your payment provider's API
    # For now, we'll return mock data
    revenue_data = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Mock revenue calculation
        basic_revenue = Subscription.query.filter(
            Subscription.plan == 'basic',
            Subscription.status == 'active',
            Subscription.created_at < next_date
        ).count() * 99  # ₹99 per month
        
        pro_revenue = Subscription.query.filter(
            Subscription.plan == 'pro',
            Subscription.status == 'active',
            Subscription.created_at < next_date
        ).count() * 299  # ₹299 per month
        
        premium_revenue = Subscription.query.filter(
            Subscription.plan == 'premium',
            Subscription.status == 'active',
            Subscription.created_at < next_date
        ).count() * 499  # ₹499 per month
        
        total_revenue = basic_revenue + pro_revenue + premium_revenue
        
        revenue_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'basic_revenue': basic_revenue,
            'pro_revenue': pro_revenue,
            'premium_revenue': premium_revenue,
            'total_revenue': total_revenue
        })
        
        current_date = next_date
    
    return revenue_data
