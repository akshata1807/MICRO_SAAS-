from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Invoice, QRCode, Resume, Certificate, Subscription, AdminUser, db
from app import login_manager
from datetime import datetime, timedelta
import os
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

# This will be handled in the main app's user_loader

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and hasattr(current_user, 'is_super_admin'):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin = AdminUser.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials!', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Admin logged out successfully!', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get statistics
    total_users = User.query.count()
    total_invoices = Invoice.query.count()
    total_resumes = Resume.query.count()
    total_certificates = Certificate.query.count()
    total_qrcodes = QRCode.query.count()
    total_subscriptions = Subscription.query.count()
    
    # Recent users (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.id.isnot(None)).order_by(desc(User.id)).limit(5).all()
    
    # Most active users (by file count)
    active_users = db.session.query(
        User.username, 
        func.count(Invoice.id).label('invoice_count'),
        func.count(Resume.id).label('resume_count'),
        func.count(Certificate.id).label('certificate_count'),
        func.count(QRCode.id).label('qrcode_count')
    ).outerjoin(Invoice).outerjoin(Resume).outerjoin(Certificate).outerjoin(QRCode)\
    .group_by(User.id, User.username)\
    .order_by(desc(func.count(Invoice.id) + func.count(Resume.id) + func.count(Certificate.id) + func.count(QRCode.id)))\
    .limit(10).all()
    
    # Daily stats for the last 7 days
    daily_stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_users = User.query.filter(User.id.isnot(None)).count()
        day_invoices = Invoice.query.filter(Invoice.created_at >= day_start, Invoice.created_at < day_end).count()
        day_resumes = Resume.query.filter(Resume.created_at >= day_start, Resume.created_at < day_end).count()
        day_certificates = Certificate.query.filter(Certificate.created_at >= day_start, Certificate.created_at < day_end).count()
        
        daily_stats.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'users': day_users,
            'invoices': day_invoices,
            'resumes': day_resumes,
            'certificates': day_certificates
        })
    
    stats = {
        'total_users': total_users,
        'total_invoices': total_invoices,
        'total_resumes': total_resumes,
        'total_certificates': total_certificates,
        'total_qrcodes': total_qrcodes,
        'total_subscriptions': total_subscriptions,
        'recent_users': recent_users,
        'active_users': active_users,
        'daily_stats': daily_stats
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/users')
@login_required
def users():
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/toggle')
@login_required
def toggle_user(user_id):
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    # Add is_active field to User model if not exists
    if not hasattr(user, 'is_active'):
        user.is_active = True
    else:
        user.is_active = not user.is_active
    
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.username} has been {status}!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's files
    for invoice in user.invoices:
        if invoice.pdf_path and os.path.exists(invoice.pdf_path):
            os.remove(invoice.pdf_path)
    
    for resume in user.resumes:
        if resume.pdf_path and os.path.exists(resume.pdf_path):
            os.remove(resume.pdf_path)
    
    for certificate in user.certificates:
        if certificate.pdf_path and os.path.exists(certificate.pdf_path):
            os.remove(certificate.pdf_path)
    
    # Delete user and related data
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} and all their data have been deleted!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/files')
@login_required
def files():
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    file_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    
    if file_type == 'invoices':
        files = Invoice.query.paginate(page=page, per_page=20, error_out=False)
    elif file_type == 'resumes':
        files = Resume.query.paginate(page=page, per_page=20, error_out=False)
    elif file_type == 'certificates':
        files = Certificate.query.paginate(page=page, per_page=20, error_out=False)
    elif file_type == 'qrcodes':
        files = QRCode.query.paginate(page=page, per_page=20, error_out=False)
    else:
        # Show all files - this would need a more complex query
        files = Invoice.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/files.html', files=files, file_type=file_type)

@admin_bp.route('/admin/subscriptions')
@login_required
def subscriptions():
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    subscriptions = Subscription.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/subscriptions.html', subscriptions=subscriptions)

@admin_bp.route('/admin/settings')
@login_required
def settings():
    if not hasattr(current_user, 'is_super_admin'):
        flash('Access denied! Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('admin/settings.html')

@admin_bp.route('/admin/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not hasattr(current_user, 'is_super_admin') or not current_user.is_super_admin:
        flash('Access denied! Super admin access required.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_super_admin = request.form.get('is_super_admin') == 'on'
        
        if AdminUser.query.filter_by(email=email).first():
            flash('Admin with this email already exists!', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        hashed_password = generate_password_hash(password)
        admin = AdminUser(
            username=username,
            email=email,
            password=hashed_password,
            is_super_admin=is_super_admin
        )
        
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin user created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_admin.html')
