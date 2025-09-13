from flask import Blueprint, render_template, flash, send_file, current_app, url_for, request
from flask_login import login_required, current_user
from app.forms import InvoiceForm, QRCodeForm, ResumeForm, CertificateForm
from app.models import Invoice, Resume, Certificate, QRCode, Template
from app.subscription_utils import subscription_required, check_usage_limit, can_use_premium_template, get_user_limits
from io import BytesIO
from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, Image as RLImage)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
from app import db
import qrcode
import tempfile
import base64

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get file counts for the current user
    invoice_count = Invoice.query.filter_by(user_id=current_user.id).count()
    resume_count = Resume.query.filter_by(user_id=current_user.id).count()
    certificate_count = Certificate.query.filter_by(user_id=current_user.id).count()
    qrcode_count = QRCode.query.filter_by(user_id=current_user.id).count()
    
    # Get recent files
    recent_invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.created_at.desc()).limit(5).all()
    recent_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).limit(5).all()
    recent_certificates = Certificate.query.filter_by(user_id=current_user.id).order_by(Certificate.created_at.desc()).limit(5).all()
    recent_qrcodes = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         invoice_count=invoice_count,
                         resume_count=resume_count,
                         certificate_count=certificate_count,
                         qrcode_count=qrcode_count,
                         recent_invoices=recent_invoices,
                         recent_resumes=recent_resumes,
                         recent_certificates=recent_certificates,
                         recent_qrcodes=recent_qrcodes)

# Improved Invoice Generator
@main_bp.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice():
    # Check usage limit
    can_create, message = check_usage_limit('invoice')
    if not can_create:
        flash(message, 'warning')
        return redirect(url_for('billing.subscribe'))
    
    # Get available templates
    available_templates = Template.query.filter_by(type='invoice', is_active=True).all()
    free_templates = [t for t in available_templates if not t.is_premium]
    premium_templates = [t for t in available_templates if t.is_premium]
    
    form = InvoiceForm()
    if form.validate_on_submit():
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']
            heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], spaceAfter=12)
            small_muted = ParagraphStyle('SmallMuted', parent=normal_style, fontSize=9, textColor=colors.HexColor('#667085'))
            label_style = ParagraphStyle('Label', parent=normal_style, textColor=colors.HexColor('#475467'), fontName='Helvetica-Bold')

            flowables = []

            # Compute available content width (points)
            content_width = doc.width
            # Timestamp-based invoice number (you can replace with DB sequence later)
            now_dt = datetime.now()
            invoice_no = str(int(now_dt.timestamp()))

            # Centered header: Company, GST, Invoice, Date
            logo_path = os.path.join(current_app.root_path, 'static', 'logo.png')
            header_flow = []
            if os.path.exists(logo_path):
                try:
                    img = RLImage(logo_path, width=1.2*inch, height=1.2*inch)
                    # Center image using single-cell table
                    img_tbl = Table([[img]], colWidths=[content_width])
                    img_tbl.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
                    header_flow.append(img_tbl)
                    header_flow.append(Spacer(1, 6))
                except Exception:
                    pass

            # Order: Invoice (line), Company (line), GST centered, Date right aligned
            header_flow.append(Paragraph('INVOICE', ParagraphStyle('InvCenter', parent=title_style, fontSize=32, leading=36, alignment=TA_CENTER, fontName='Helvetica-Bold')))
            # Line below Invoice
            inv_line = Table([[""]], colWidths=[content_width])
            inv_line.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 1.2, colors.HexColor('#0B5394'))]))
            header_flow.append(inv_line)
            header_flow.append(Spacer(1, 6))

            header_flow.append(Paragraph(form.company.data, ParagraphStyle('HCenter', parent=title_style, fontSize=28, leading=32, alignment=TA_CENTER)))
            # Date centered directly below the company name line
            header_flow.append(Paragraph(now_dt.strftime('%d-%m-%Y'), ParagraphStyle('DateCenter', parent=small_muted, alignment=TA_CENTER)))
            # Invoice number centered just below date
            header_flow.append(Paragraph(f"Invoice #: {invoice_no}", ParagraphStyle('InvNumCenter', parent=small_muted, alignment=TA_CENTER)))
            header_flow.append(Spacer(1, 6))

            header_table = Table([[header_flow]], colWidths=[content_width])
            header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
            flowables.append(header_table)
            flowables.append(Spacer(1, 14))

            # Header info grid like template (top-right info)
            due_dt = now_dt.strftime('%d-%m-%Y')
            info_rows = [
                [Paragraph('DATE', label_style), Paragraph(now_dt.strftime('%d-%m-%Y'), normal_style)],
            ]
            # Date already shown under company name

            flowables.append(Spacer(1, 12))

            # BILL TO heading bar
            bill_bar = Table([[Paragraph('BILL TO', ParagraphStyle('BillBar', parent=normal_style, fontName='Helvetica-Bold', textColor=colors.white))]], colWidths=[content_width*0.48], hAlign='LEFT')
            bill_bar.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0B5394')),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4)
            ]))
            flowables.append(bill_bar)

            # Bill-to block under the bar
            details_widths = [content_width * 0.18, content_width * 0.30]
            details_rows = [
                [Paragraph('Company:', label_style), Paragraph(form.company.data, normal_style)],
                [Paragraph('GST Number:', label_style), Paragraph(form.gst.data, normal_style)],
                [Paragraph('Bill To:', label_style), Paragraph(form.client.data, normal_style)],
            ]
            details_table = Table(details_rows, colWidths=details_widths, hAlign='LEFT')
            details_table.setStyle(TableStyle([
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4)
            ]))
            flowables.append(details_table)
            flowables.append(Spacer(1, 12))

            # Spacer before items table
            flowables.append(Spacer(1, 12))

            def format_amount(value):
                try:
                    # Use Rs. to avoid missing glyphs in base PDF fonts
                    return f"Rs. {float(value):,.2f}"
                except Exception:
                    return value

            data = [['DESCRIPTION', 'AMOUNT (INR)']]
            items = [item.strip() for item in form.items.data.replace(',', '\n').split('\n') if item.strip()]
            computed_total = 0.0
            for item in items:
                if '-' in item:
                    parts = item.split('-', 1)
                    description = parts[0].strip()
                    amount_str = parts[1].strip()
                    try:
                        computed_total += float(amount_str)
                    except Exception:
                        pass
                    data.append([Paragraph(description, normal_style), Paragraph(format_amount(amount_str), ParagraphStyle('Right', parent=normal_style, alignment=TA_RIGHT))])
                else:
                    data.append([Paragraph(item, normal_style), ''])

            items_left = content_width * 0.70
            items_right = content_width - items_left
            items_table = Table(data, colWidths=[items_left, items_right])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0B5394')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('TOPPADDING', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('LEFTPADDING', (0,1), (-1,-1), 10),
                ('RIGHTPADDING', (0,1), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#E6EAF2')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
            ]))
            flowables.append(items_table)

            # Totals row aligned with items table columns
            flowables.append(Spacer(1, 12))
            total_value = form.total.data if form.total.data else computed_total
            totals_table = Table([
                [Paragraph('TOTAL', ParagraphStyle('TotalLabel', parent=normal_style, fontName='Helvetica-Bold', alignment=TA_RIGHT)),
                 Paragraph(format_amount(total_value), ParagraphStyle('TotalRight', parent=normal_style, alignment=TA_RIGHT, fontName='Helvetica-Bold'))]
            ], colWidths=[items_left, items_right])
            totals_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF4FF')),
                ('LINEABOVE', (0,0), (-1,0), 0.75, colors.HexColor('#D0D5DD')),
                ('LINEBELOW', (0,0), (-1,0), 0.75, colors.HexColor('#D0D5DD')),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10)
            ]))
            flowables.append(totals_table)

            # Footer note
            flowables.append(Spacer(1, 18))
            flowables.append(Paragraph("Thank you for your business", ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, textColor=colors.HexColor('#475467'))))

            doc.build(flowables)
            buffer.seek(0)

            filename = f"invoice_{current_user.id}_{int(datetime.utcnow().timestamp())}.pdf"
            invoices_dir = os.path.join(current_app.root_path, 'static', 'invoices')
            os.makedirs(invoices_dir, exist_ok=True)
            save_path = os.path.join(invoices_dir, filename)

            with open(save_path, 'wb') as f:
                f.write(buffer.getbuffer())

            invoice = Invoice(
                user_id=current_user.id,
                company=form.company.data,
                client=form.client.data,
                gst=form.gst.data,
                items=form.items.data,
                total=form.total.data,
                pdf_path=save_path
            )
            db.session.add(invoice)
            db.session.commit()

            flash('Invoice generated successfully!', 'success')
            return send_file(save_path, as_attachment=True)

        except Exception as e:
            flash(f"Error generating invoice: {e}", 'danger')

    return render_template('invoice.html', form=form, 
                         free_templates=free_templates, 
                         premium_templates=premium_templates,
                         can_use_premium=can_use_premium_template(),
                         user_limits=get_user_limits())

@main_bp.route('/invoices')
@login_required
def invoices():
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('invoices.html', invoices=invoices)

# QR Code Generator - Inline display with download link
@main_bp.route('/qrcode', methods=['GET', 'POST'])
@login_required
def qrcode_generator():
    form = QRCodeForm()
    qr_img_data = None
    if form.validate_on_submit():
        data = form.data.data

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        qr_img_data = f"data:image/png;base64,{img_base64}"

        # Save QR code to database
        filename = f"qrcode_{current_user.id}_{int(datetime.utcnow().timestamp())}.png"
        qrcodes_dir = os.path.join(current_app.root_path, 'static', 'qrcodes')
        os.makedirs(qrcodes_dir, exist_ok=True)
        save_path = os.path.join(qrcodes_dir, filename)
        
        # Save the image to file
        img.save(save_path)
        
        # Save to database
        qr_record = QRCode(
            user_id=current_user.id,
            data=data,
            img_path=save_path
        )
        db.session.add(qr_record)
        db.session.commit()

    return render_template('qrcode.html', form=form, qr_img_data=qr_img_data)

# Resume Builder with professional styling
@main_bp.route('/resume', methods=['GET', 'POST'])
@login_required
def resume_builder():
    form = ResumeForm()
    if form.validate_on_submit():
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=LETTER,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()

            name_style = ParagraphStyle(
                'NameStyle', parent=styles['Title'], fontSize=24, leading=28,
                alignment=TA_CENTER, spaceAfter=20)

            contact_style = ParagraphStyle(
                'ContactStyle', parent=styles['Normal'], fontSize=10, leading=12,
                alignment=TA_CENTER, textColor='#555555', spaceAfter=24)

            section_header_style = ParagraphStyle(
                'SectionHeader', parent=styles['Heading2'], fontSize=14,
                textColor='#0B5394', spaceBefore=12, spaceAfter=8,
                alignment=TA_LEFT)

            body_text_style = ParagraphStyle(
                'BodyText', parent=styles['BodyText'], fontSize=12,
                leading=16, spaceAfter=6, alignment=TA_LEFT)

            flowables = []

            flowables.append(Paragraph(form.name.data, name_style))

            contact_info = f"{form.email.data}"
            if form.phone.data:
                contact_info += f" | {form.phone.data}"
            flowables.append(Paragraph(contact_info, contact_style))

            # Divider
            flowables.append(Table(
                [['']], colWidths=[6*inch],
                style=[('LINEABOVE', (0,0), (-1,-1), 1.2, '#0B5394')],
                spaceBefore=0, spaceAfter=12
            ))

            def add_section(title, content):
                flowables.append(Paragraph(title, section_header_style))
                if not content.strip():
                    flowables.append(Paragraph("N/A", body_text_style))
                    return
                bullets = [line.strip() for line in content.strip().split('\n') if line.strip()]
                bullet_items = [ListItem(Paragraph(line, body_text_style)) for line in bullets]
                flowables.append(ListFlowable(bullet_items, bulletType='bullet', start='circle'))

            add_section("Education", form.education.data)
            add_section("Skills", form.skills.data)
            add_section("Experience", form.experience.data)

            doc.build(flowables)
            buffer.seek(0)

            filename = f"resume_{current_user.id}_{int(datetime.utcnow().timestamp())}.pdf"
            resumes_dir = os.path.join(current_app.root_path, 'static', 'resumes')
            os.makedirs(resumes_dir, exist_ok=True)
            save_path = os.path.join(resumes_dir, filename)

            with open(save_path, 'wb') as f:
                f.write(buffer.getbuffer())

            # Save resume to database
            resume = Resume(
                user_id=current_user.id,
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                education=form.education.data,
                skills=form.skills.data,
                experience=form.experience.data,
                pdf_path=save_path
            )
            db.session.add(resume)
            db.session.commit()

            flash('Resume generated successfully!', 'success')
            return send_file(save_path, as_attachment=True, download_name='resume.pdf')

        except Exception as e:
            flash(f'An error occurred while generating the resume: {e}', 'danger')

    return render_template('resume.html', form=form)


# Certificate Generator - Professional PDF with border
@main_bp.route('/certificate', methods=['GET', 'POST'])
@login_required
def certificate_generator():
    form = CertificateForm()
    if form.validate_on_submit():
        try:
            buffer = BytesIO()
            page_size = landscape(A4)
            doc = SimpleDocTemplate(
                buffer,
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
            flowables.append(Paragraph(form.recipient_name.data, name_style))
            flowables.append(Paragraph('has successfully completed', subtitle_style))
            flowables.append(Paragraph(form.course_title.data, ParagraphStyle('Course', parent=title_style, fontSize=22, leading=26)))
            flowables.append(Spacer(1, 12))
            flowables.append(Paragraph(f"Issued by {form.issuer.data} on {form.date_issued.data}", body_style))

            # Signature section
            sig_name = form.signature_name.data.strip() if form.signature_name.data else ''
            sig_title = form.signature_title.data.strip() if form.signature_title.data else ''
            if sig_name:
                flowables.append(Spacer(1, 24))
                sig_table = Table(
                    [[Paragraph(sig_name, body_style)], [Paragraph(sig_title or '', body_style)]],
                    colWidths=[4*inch]
                )
                sig_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('LINEABOVE', (0, 0), (-1, 0), 0.8, colors.HexColor('#0B5394')),
                ]))
                flowables.append(sig_table)

            # Draw decorative border on each page
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
            buffer.seek(0)

            filename = f"certificate_{current_user.id}_{int(datetime.utcnow().timestamp())}.pdf"
            certs_dir = os.path.join(current_app.root_path, 'static', 'certificates')
            os.makedirs(certs_dir, exist_ok=True)
            save_path = os.path.join(certs_dir, filename)
            with open(save_path, 'wb') as f:
                f.write(buffer.getbuffer())

            # Save certificate to database
            certificate = Certificate(
                user_id=current_user.id,
                recipient_name=form.recipient_name.data,
                course_title=form.course_title.data,
                issuer=form.issuer.data,
                date_issued=form.date_issued.data,
                signature_name=form.signature_name.data,
                signature_title=form.signature_title.data,
                pdf_path=save_path
            )
            db.session.add(certificate)
            db.session.commit()

            flash('Certificate generated successfully!', 'success')
            return send_file(save_path, as_attachment=True, download_name='certificate.pdf')
        except Exception as e:
            flash(f'Error generating certificate: {e}', 'danger')

    return render_template('certificate.html', form=form)


import json
from flask import request, abort
import stripe

@main_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        abort(400)

    # Handle subscription events
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        # Update your database accordingly
        # e.g. save stripe_subscription_id, status, etc.

    # handle other events like 'customer.subscription.deleted', 'payment_failed' etc.

    return '', 200
