"""
Email verification and notification utilities
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
from flask_mail import Mail, Message
import secrets
import string
from datetime import datetime, timedelta
from app.models import User, db

# Initialize Flask-Mail
mail = Mail()

def generate_verification_token():
    """Generate a secure verification token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def send_verification_email(user):
    """Send email verification to user"""
    try:
        # Generate verification token
        token = generate_verification_token()
        user.verification_token = token
        user.token_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        # Create verification link
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        
        # Create email content
        subject = "Verify Your MicroSaaS Account"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0b63f6 0%, #1f2dd6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Welcome to MicroSaaS!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Please verify your email address to get started</p>
            </div>
            
            <div style="background: white; padding: 30px; border: 1px solid #e6eaf2; border-radius: 0 0 10px 10px;">
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Hi {user.username},
                </p>
                
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Thank you for signing up for MicroSaaS! To complete your registration and start using our tools, 
                    please verify your email address by clicking the button below:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background: #0b63f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                
                <p style="color: #667085; font-size: 14px; line-height: 1.6;">
                    If the button doesn't work, you can copy and paste this link into your browser:
                </p>
                <p style="color: #0b63f6; font-size: 14px; word-break: break-all;">
                    {verification_url}
                </p>
                
                <p style="color: #667085; font-size: 14px; line-height: 1.6;">
                    This link will expire in 24 hours. If you didn't create an account with MicroSaaS, 
                    please ignore this email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e6eaf2; margin: 30px 0;">
                
                <p style="color: #667085; font-size: 12px; text-align: center;">
                    © 2025 MicroSaaS. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to MicroSaaS!
        
        Hi {user.username},
        
        Thank you for signing up for MicroSaaS! To complete your registration and start using our tools, 
        please verify your email address by visiting this link:
        
        {verification_url}
        
        This link will expire in 24 hours. If you didn't create an account with MicroSaaS, 
        please ignore this email.
        
        Best regards,
        The MicroSaaS Team
        """
        
        # Send email
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def send_welcome_email(user):
    """Send welcome email after verification"""
    try:
        subject = "Welcome to MicroSaaS - Let's Get Started!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0b63f6 0%, #1f2dd6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Welcome to MicroSaaS!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Your account is now verified and ready to use</p>
            </div>
            
            <div style="background: white; padding: 30px; border: 1px solid #e6eaf2; border-radius: 0 0 10px 10px;">
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Hi {user.username},
                </p>
                
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Congratulations! Your MicroSaaS account has been verified and you're ready to start creating 
                    professional documents in minutes.
                </p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1f2937; margin-top: 0;">What you can do:</h3>
                    <ul style="color: #475467; line-height: 1.8;">
                        <li>Generate professional invoices with your branding</li>
                        <li>Create clean, modern resumes in PDF format</li>
                        <li>Design certificates of completion</li>
                        <li>Generate QR codes for any text or URL</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_for('main.dashboard', _external=True)}" 
                       style="background: #0b63f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Go to Dashboard
                    </a>
                </div>
                
                <p style="color: #667085; font-size: 14px; line-height: 1.6;">
                    Need help getting started? Check out our 
                    <a href="{url_for('main.index', _external=True)}" style="color: #0b63f6;">help center</a> 
                    or reply to this email if you have any questions.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e6eaf2; margin: 30px 0;">
                
                <p style="color: #667085; font-size: 12px; text-align: center;">
                    © 2025 MicroSaaS. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False

def send_subscription_confirmation(user, plan):
    """Send subscription confirmation email"""
    try:
        subject = f"Subscription Confirmed - {plan.title()} Plan"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0b63f6 0%, #1f2dd6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">Subscription Confirmed!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">You're now on the {plan.title()} plan</p>
            </div>
            
            <div style="background: white; padding: 30px; border: 1px solid #e6eaf2; border-radius: 0 0 10px 10px;">
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Hi {user.username},
                </p>
                
                <p style="color: #1f2937; font-size: 16px; line-height: 1.6;">
                    Thank you for upgrading to our {plan.title()} plan! You now have access to premium features 
                    and higher usage limits.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_for('main.dashboard', _external=True)}" 
                       style="background: #0b63f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Access Your Dashboard
                    </a>
                </div>
                
                <p style="color: #667085; font-size: 12px; text-align: center;">
                    © 2025 MicroSaaS. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending subscription confirmation: {e}")
        return False
