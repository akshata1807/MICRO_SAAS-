from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


from wtforms import TextAreaField, FloatField

class InvoiceForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    client = StringField('Client', validators=[DataRequired()])
    gst = StringField('GST Number', validators=[DataRequired()])
    items = TextAreaField('Items (one per line)', validators=[DataRequired()])
    total = FloatField('Total Amount', validators=[DataRequired()])
    submit = SubmitField('Generate Invoice')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL

class QRCodeForm(FlaskForm):
    data = StringField('Enter URL or Text', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Generate QR Code')

#Resume Builder
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email

class ResumeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    education = TextAreaField('Education', validators=[Optional(), Length(max=1000)])
    skills = TextAreaField('Skills', validators=[Optional(), Length(max=1000)])
    experience = TextAreaField('Experience', validators=[Optional(), Length(max=1500)])
    submit = SubmitField('Generate Resume')

# Certificate Generator
from wtforms.fields import DateField

class CertificateForm(FlaskForm):
    recipient_name = StringField('Recipient Name', validators=[DataRequired(), Length(max=100)])
    course_title = StringField('Course/Program Title', validators=[DataRequired(), Length(max=150)])
    issuer = StringField('Issuer/Organization', validators=[DataRequired(), Length(max=120)])
    date_issued = StringField('Date (e.g., 10 Sep 2025)', validators=[DataRequired(), Length(max=40)])
    signature_name = StringField('Signer Name', validators=[Optional(), Length(max=100)])
    signature_title = StringField('Signer Title', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Generate Certificate')