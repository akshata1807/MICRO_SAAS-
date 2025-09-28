# Micro SaaS Platform

A comprehensive SaaS platform built with Flask that provides multiple business tools including Invoice Generator, Resume Builder, Certificate Creator, and QR Code Maker. Features user authentication, subscription management, admin panel, and analytics.

## Features

### Core Tools
- **Invoice Generator**: Create professional invoices with GST support, PDF generation, and client management
- **Resume Builder**: Build and customize professional resumes with PDF export
- **Certificate Creator**: Generate certificates with customizable templates and bulk creation
- **QR Code Maker**: Create QR codes for various data types with image export

### Platform Features
- **User Authentication**: Secure login/registration with email verification
- **Subscription Management**: Multiple tiers (Free, Basic, Pro, Premium) with Stripe integration
- **Admin Panel**: Comprehensive admin dashboard for user management and analytics
- **Analytics Dashboard**: Track usage statistics and platform metrics
- **Bulk Operations**: Process multiple certificates and documents efficiently
- **Email Notifications**: Automated email system for user communications
- **Rate Limiting**: Security features to prevent abuse
- **File Upload**: Support for various file formats (PDF, images, spreadsheets)

## Tech Stack

- **Backend**: Flask 3.1.2, Python
- **Database**: SQLAlchemy 2.0.43, SQLite/PostgreSQL
- **Authentication**: Flask-Login
- **Payments**: Stripe API
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode library, Pillow
- **Email**: Flask-Mail
- **Security**: Flask-Limiter, Flask-Bcrypt
- **Frontend**: Jinja2 templates, Bootstrap CSS
- **Forms**: Flask-WTF, WTForms

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd micro-saas-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_complete.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///site.db
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   STRIPE_WEBHOOK_SECRET=your-webhook-secret
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Database Setup**
   ```bash
   python create_db.py
   python migrate_database.py
   ```

6. **Create Admin User** (Optional)
   ```bash
   python create_admin_user.py
   ```

## Usage

### Running the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

### User Registration & Login
- Register a new account or login with existing credentials
- Verify email address for full access
- Choose subscription plan (Free/Basic/Pro/Premium)

### Using the Tools

#### Invoice Generator
1. Login to your account
2. Navigate to Invoice section
3. Fill in company details, client information, and GST
4. Add invoice items with quantities and prices
5. Generate and download PDF

#### Resume Builder
1. Access Resume Builder from dashboard
2. Enter personal information, education, skills, and experience
3. Customize template and layout
4. Export as PDF

#### Certificate Creator
1. Go to Certificate section
2. Enter recipient details, course information, and issuer
3. Add signature details
4. Generate certificate PDF

#### QR Code Maker
1. Navigate to QR Code tool
2. Enter data (URL, text, contact info, etc.)
3. Customize size and format
4. Download QR code image

### Admin Panel
Access admin features at `/admin` with admin credentials:
- User management
- Subscription oversight
- Analytics viewing
- Bulk operations
- System settings

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `POST /logout` - User logout

### Tools
- `GET/POST /invoice` - Invoice generation
- `GET/POST /resume` - Resume builder
- `GET/POST /certificate` - Certificate creation
- `GET/POST /qrcode` - QR code generation

### Subscriptions
- `POST /subscribe` - Create subscription
- `POST /webhook` - Stripe webhook handler

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/analytics` - Analytics view

## Database Models

- **User**: Regular users with subscription status
- **AdminUser**: Administrative users
- **Invoice**: Generated invoices
- **Resume**: Created resumes
- **Certificate**: Generated certificates
- **QRCode**: Created QR codes
- **Subscription**: User subscriptions
- **Template**: Document templates

## Configuration

Key configuration options in `config.py`:
- Database URI
- Stripe API keys
- Email settings
- Security settings
- File upload limits

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

### Database Migrations
```bash
python migrate_database.py
```

## Deployment

### Environment Variables
Ensure all required environment variables are set for production:
- Database URL (PostgreSQL recommended)
- Stripe live keys
- Email credentials
- Secret keys

### Production Setup
1. Set `DEBUG=False` in Flask config
2. Use a production WSGI server (gunicorn, uwsgi)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure database backups

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Use descriptive commit messages
- Write tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.


