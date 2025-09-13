# Admin Panel Setup Guide

## 🚀 Quick Start

### 1. Update Database
First, update your database with the new models:

```bash
python update_database.py
```

### 2. Create Admin User
Create your first admin user:

```bash
python create_admin_user.py
```

Follow the prompts to set up your admin credentials.

### 3. Run the Application
Start your Flask application:

```bash
python run.py
```

### 4. Access Admin Panel
Navigate to: `http://localhost:5000/admin/login`

## 🔧 Admin Panel Features

### Dashboard
- **Statistics Overview**: Total users, files, subscriptions
- **Recent Users**: Latest registered users
- **Most Active Users**: Users with most file activity
- **Daily Statistics**: Activity over the last 7 days
- **Quick Actions**: Direct links to management sections

### User Management
- **View All Users**: Paginated list of all users
- **User Details**: Username, email, file counts, status
- **Toggle User Status**: Activate/deactivate users
- **Delete Users**: Remove users and their files
- **File Statistics**: See how many files each user has created

### File Management
- **Filter by Type**: View invoices, resumes, certificates, or QR codes
- **File Details**: User info, creation date, file content preview
- **Download Files**: Direct download links for generated files
- **File Statistics**: Total files, pagination info

### Subscription Management
- **View Subscriptions**: All user subscriptions with details
- **Plan Information**: Basic, Pro, Premium plan distribution
- **Status Tracking**: Active, canceled, expired subscriptions
- **Revenue Overview**: Subscription statistics and analytics

### Settings
- **System Information**: Database, Python, Flask versions
- **Security Status**: Admin access, authentication status
- **Maintenance Actions**: Backup, cleanup, reports (demo mode)

### Admin User Management
- **Create Admins**: Add new admin users
- **Super Admin Access**: Full system access
- **Regular Admin Access**: Limited admin features
- **Security Guidelines**: Best practices for admin management

## 🎨 Theme & Styling

The admin panel uses the same theme as your main application:
- **Color Scheme**: Blue gradient (#0b63f6 to #1f2dd6)
- **Typography**: Clean, modern fonts
- **Cards**: Rounded corners with subtle shadows
- **Icons**: Font Awesome icons throughout
- **Responsive**: Mobile-friendly design

## 🔐 Security Features

- **Admin Authentication**: Separate login system for admins
- **Access Control**: Super admin vs regular admin permissions
- **User Management**: Safe user activation/deactivation
- **File Security**: Secure file access and downloads
- **Session Management**: Proper login/logout handling

## 📊 Database Models

### New Models Added:
- **Resume**: Stores resume data and PDF paths
- **Certificate**: Stores certificate data and PDF paths
- **AdminUser**: Admin user accounts with permissions

### Updated Models:
- **User**: Enhanced with file relationships
- **Invoice**: Already existed, now properly linked
- **QRCode**: Already existed, now properly linked

## 🚨 Important Notes

1. **First Admin**: Create the first admin user using the script
2. **Super Admin**: Only super admins can create other admins
3. **File Storage**: Files are stored in the `static/` directory
4. **Database**: Uses SQLite for development (easily changeable)
5. **Security**: Admin panel is protected and requires authentication

## 🔄 Next Steps

1. **Test the Admin Panel**: Login and explore all features
2. **Create Test Data**: Generate some files to see in admin panel
3. **Customize Settings**: Adjust any settings as needed
4. **Add More Admins**: Create additional admin users if needed
5. **Monitor Usage**: Use the dashboard to track user activity

## 🆘 Troubleshooting

### Common Issues:

1. **Database Errors**: Run `update_database.py` first
2. **Admin Login Issues**: Check admin user was created properly
3. **File Access Issues**: Ensure static directory permissions are correct
4. **Template Errors**: Check all admin templates are in place

### Support:
- Check the console for error messages
- Verify all files are in the correct locations
- Ensure database is properly initialized

---

**Admin Panel Ready!** 🎉
Your MicroSaaS platform now has a complete admin panel with user management, file tracking, and analytics.
