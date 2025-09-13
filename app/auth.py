from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .forms import RegistrationForm, LoginForm
from . import db
from .email_utils import send_verification_email, send_welcome_email
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if send_verification_email(user):
            flash('Account Created! Please check your email to verify your account.', 'success')
        else:
            flash('Account Created! Please check your email to verify your account. (Email sending failed)', 'warning')
        
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))
    
    if user.token_expires and user.token_expires < datetime.utcnow():
        flash('Verification link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.login'))
    
    user.is_verified = True
    user.verification_token = None
    user.token_expires = None
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(user)
    
    flash('Email verified successfully! Welcome to MicroSaaS!', 'success')
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/resend-verification')
def resend_verification():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if send_verification_email(current_user):
        flash('Verification email sent! Please check your inbox.', 'success')
    else:
        flash('Failed to send verification email. Please try again.', 'danger')
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
