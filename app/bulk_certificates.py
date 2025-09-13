"""
Bulk certificate generation with Excel upload
"""
from flask import Blueprint, render_template, request, flash, send_file, current_app, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# import pandas as pd  # Commented out for now due to build issues
import os
import zipfile
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from app.subscription_utils import can_use_bulk_operations, check_usage_limit
from app.models import Certificate, db

bulk_bp = Blueprint('bulk', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bulk_bp.route('/bulk-certificates', methods=['GET', 'POST'])
@login_required
def bulk_certificates():
    if not can_use_bulk_operations():
        flash('Bulk operations require a Pro or Premium subscription. Please upgrade your plan.', 'warning')
        return redirect(url_for('billing.subscribe'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # For now, we'll use a simple CSV approach instead of pandas
                # Read CSV file
                file_content = file.read().decode('utf-8')
                lines = file_content.strip().split('\n')
                
                if len(lines) < 2:
                    flash('File must contain at least a header row and one data row', 'error')
                    return redirect(request.url)
                
                # Parse header
                headers = [h.strip() for h in lines[0].split(',')]
                required_columns = ['recipient_name', 'course_title', 'issuer', 'date_issued']
                missing_columns = [col for col in required_columns if col not in headers]
                
                if missing_columns:
                    flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
                    return redirect(request.url)
                
                # Parse data rows
                certificates = []
                for i, line in enumerate(lines[1:], 1):
                    values = [v.strip() for v in line.split(',')]
                    if len(values) != len(headers):
                        flash(f'Row {i+1} has incorrect number of columns', 'error')
                        return redirect(request.url)
                    
                    # Create dictionary from headers and values
                    row_data = dict(zip(headers, values))
                    
                    certificate_data = {
                        'recipient_name': str(row_data.get('recipient_name', '')),
                        'course_title': str(row_data.get('course_title', '')),
                        'issuer': str(row_data.get('issuer', '')),
                        'date_issued': str(row_data.get('date_issued', '')),
                        'signature_name': str(row_data.get('signature_name', '')),
                        'signature_title': str(row_data.get('signature_title', ''))
                    }
                    certificates.append(certificate_data)
                
                # Check usage limit
                can_create, message = check_usage_limit('certificate')
                if not can_create:
                    flash(f'Cannot create {len(certificates)} certificates: {message}', 'warning')
                    return redirect(request.url)
                
                # Create ZIP file with all certificates
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, cert_data in enumerate(certificates):
                        # Generate PDF for each certificate
                        pdf_buffer = BytesIO()
                        page_size = landscape(A4)
                        doc = SimpleDocTemplate(
                            pdf_buffer,
                            pagesize=page_size,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=72
                        )
                        
                        styles = getSampleStyleSheet()
                        title_style = ParagraphStyle(
                            'CertTitle', parent=styles['Title'], fontSize=32, leading=36,
                            alignment=TA_CENTER, textColor=colors.HexColor('#0B5394'), spaceAfter=18
                        )
                        subtitle_style = ParagraphStyle(
                            'Subtitle', parent=styles['Heading2'], fontSize=14, leading=18,
                            alignment=TA_CENTER, textColor=colors.HexColor('#475467'), spaceAfter=6
                        )
                        name_style = ParagraphStyle(
                            'Name', parent=styles['Title'], fontSize=28, leading=32,
                            alignment=TA_CENTER, textColor=colors.HexColor('#1F2937'), spaceAfter=10
                        )
                        body_style = ParagraphStyle(
                            'Body', parent=styles['BodyText'], fontSize=12, leading=18,
                            alignment=TA_CENTER, textColor=colors.HexColor('#475467'), spaceAfter=16
                        )
                        
                        flowables = []
                        flowables.append(Paragraph('Certificate of Completion', title_style))
                        flowables.append(Paragraph('This is to certify that', subtitle_style))
                        flowables.append(Paragraph(cert_data['recipient_name'], name_style))
                        flowables.append(Paragraph('has successfully completed', subtitle_style))
                        flowables.append(Paragraph(cert_data['course_title'], ParagraphStyle('Course', parent=title_style, fontSize=22, leading=26)))
                        flowables.append(Spacer(1, 12))
                        flowables.append(Paragraph(f"Issued by {cert_data['issuer']} on {cert_data['date_issued']}", body_style))
                        
                        # Signature section
                        if cert_data['signature_name']:
                            flowables.append(Spacer(1, 24))
                            sig_table = Table([
                                [Paragraph(cert_data['signature_name'], body_style)], 
                                [Paragraph(cert_data['signature_title'] or '', body_style)]
                            ], colWidths=[4*inch])
                            sig_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('LINEABOVE', (0, 0), (-1, 0), 0.8, colors.HexColor('#0B5394')),
                            ]))
                            flowables.append(sig_table)
                        
                        # Draw decorative border
                        def draw_border(canvas, _doc):
                            canvas.saveState()
                            canvas.setLineWidth(5)
                            canvas.setStrokeColor(colors.HexColor('#0B5394'))
                            width, height = page_size
                            margin = 28
                            canvas.rect(margin, margin, width - 2*margin, height - 2*margin)
                            canvas.setLineWidth(1.2)
                            canvas.setStrokeColor(colors.HexColor('#D0D5DD'))
                            inner = margin + 10
                            canvas.rect(inner, inner, width - 2*inner, height - 2*inner)
                            canvas.restoreState()
                        
                        doc.build(flowables, onFirstPage=draw_border, onLaterPages=draw_border)
                        pdf_buffer.seek(0)
                        
                        # Add to ZIP
                        filename = f"certificate_{i+1}_{cert_data['recipient_name'].replace(' ', '_')}.pdf"
                        zip_file.writestr(filename, pdf_buffer.getvalue())
                        
                        # Save to database
                        cert = Certificate(
                            user_id=current_user.id,
                            recipient_name=cert_data['recipient_name'],
                            course_title=cert_data['course_title'],
                            issuer=cert_data['issuer'],
                            date_issued=cert_data['date_issued'],
                            signature_name=cert_data['signature_name'],
                            signature_title=cert_data['signature_title'],
                            pdf_path=f"bulk_certificate_{i+1}"
                        )
                        db.session.add(cert)
                
                db.session.commit()
                zip_buffer.seek(0)
                
                flash(f'Successfully generated {len(certificates)} certificates!', 'success')
                return send_file(
                    zip_buffer,
                    as_attachment=True,
                    download_name=f'certificates_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
                    mimetype='application/zip'
                )
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload an Excel file (.xlsx, .xls) or CSV file.', 'error')
            return redirect(request.url)
    
    return render_template('bulk_certificates.html')

@bulk_bp.route('/bulk-template')
@login_required
def download_template():
    """Download CSV template for bulk certificate generation"""
    if not can_use_bulk_operations():
        flash('Bulk operations require a Pro or Premium subscription. Please upgrade your plan.', 'warning')
        return redirect(url_for('billing.subscribe'))
    
    # Create CSV template
    csv_content = """recipient_name,course_title,issuer,date_issued,signature_name,signature_title
John Doe,Python Programming,Tech Academy,2025-01-15,Dr. Sarah Wilson,Course Director
Jane Smith,Web Development,Code Institute,2025-01-16,Prof. Mike Brown,Head of Department
Bob Johnson,Data Science,Data University,2025-01-17,Dr. Lisa Davis,Program Coordinator"""
    
    csv_buffer = BytesIO()
    csv_buffer.write(csv_content.encode('utf-8'))
    csv_buffer.seek(0)
    
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='certificate_template.csv',
        mimetype='text/csv'
    )
