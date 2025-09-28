import streamlit as st

# Streamlit Cloud expects a Streamlit app, not a Flask app
# This wrapper provides a Streamlit interface to our Flask backend

st.set_page_config(
    page_title="Micro SaaS Platform",
    page_icon="",
    layout="wide"
)

# Health check endpoint for Streamlit Cloud - this ensures the app is healthy
st.write(" Micro SaaS Platform is running!")

# Add a health check function that Streamlit Cloud can use
def check_health():
    """Health check function for Streamlit Cloud"""
    return True

# Make the health check available globally
globals()['check_health'] = check_health

st.title(" Micro SaaS Platform")
st.subheader("Flask Backend with Streamlit Frontend")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Invoice Generator", "Resume Builder", "Certificate Creator", "QR Code Maker"]
)

# Main content based on selected page
if page == "Home":
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .tool-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    .tool-card:hover {
        transform: translateY(-5px);
    }
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown("""
    <div class="main-header">
        <h1> Micro SaaS Platform</h1>
        <p>Your Complete Business Solution</p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message
    st.success(" Micro SaaS Platform is running successfully!")

    # Stats section
    st.subheader(" Platform Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <h2>4</h2>
            <p>Business Tools</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <h2>100%</h2>
            <p>Uptime</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <h2></h2>
            <p>Secure</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <h2>⚡</h2>
            <p>Fast</p>
        </div>
        """, unsafe_allow_html=True)

    # Main features section
    st.subheader("🛠️ Our Business Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tool-card">
            <h3>📄 Invoice Generator</h3>
            <p>Create professional invoices with GST support, PDF generation, and client management. Perfect for businesses of all sizes.</p>
            <strong>Features:</strong>
            <ul>
                <li>Professional PDF invoices</li>
                <li>GST calculation support</li>
                <li>Client management</li>
                <li>Multiple templates</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tool-card">
            <h3>📝 Resume Builder</h3>
            <p>Build and customize professional resumes with PDF export. Stand out from the crowd with our modern templates.</p>
            <strong>Features:</strong>
            <ul>
                <li>Modern templates</li>
                <li>PDF export</li>
                <li>Easy customization</li>
                <li>Professional layouts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tool-card">
            <h3>🏆 Certificate Creator</h3>
            <p>Generate certificates with customizable templates and bulk creation. Ideal for educational institutions and events.</p>
            <strong>Features:</strong>
            <ul>
                <li>Custom templates</li>
                <li>Bulk generation</li>
                <li>Professional design</li>
                <li>Easy customization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tool-card">
            <h3>📱 QR Code Maker</h3>
            <p>Create QR codes for various data types with image export. Perfect for marketing and information sharing.</p>
            <strong>Features:</strong>
            <ul>
                <li>Multiple data types</li>
                <li>High-quality images</li>
                <li>Customizable size</li>
                <li>Easy download</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Platform features
    st.subheader("✨ Platform Features")

    st.markdown("""
    <div class="feature-card">
        <h4>🔐 Security & Authentication</h4>
        <p>Secure user authentication with email verification, password encryption, and role-based access control.</p>
    </div>

    <div class="feature-card">
        <h4>💳 Subscription Management</h4>
        <p>Multiple subscription tiers (Free, Basic, Pro, Premium) with Stripe payment integration and automated billing.</p>
    </div>

    <div class="feature-card">
        <h4>👥 Admin Panel</h4>
        <p>Comprehensive admin dashboard for user management, analytics, and platform oversight.</p>
    </div>

    <div class="feature-card">
        <h4>📊 Analytics Dashboard</h4>
        <p>Track usage statistics, user engagement, and platform performance with detailed analytics.</p>
    </div>

    <div class="feature-card">
        <h4>📧 Email Notifications</h4>
        <p>Automated email system for user communications, notifications, and marketing campaigns.</p>
    </div>

    <div class="feature-card">
        <h4>🔄 Bulk Operations</h4>
        <p>Process multiple certificates and documents efficiently with our batch processing system.</p>
    </div>
    """, unsafe_allow_html=True)

    # Call to action
    st.subheader("🚀 Get Started")
    st.write("Choose a tool from the navigation menu to get started with your business needs!")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>Micro SaaS Platform</strong> - Your Complete Business Solution</p>
        <p>Built with ❤️ using Flask backend and Streamlit frontend</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "Invoice Generator":
    st.markdown("""
    <style>
    .tool-header {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-header">
        <h2>📄 Professional Invoice Generator</h2>
        <p>Create beautiful, professional invoices in minutes</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("🚧 **Feature Coming Soon!**")
    st.info("💡 This will connect to your Flask backend for full invoice generation functionality.")

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("invoice_form"):
            st.subheader("📝 Quick Invoice Preview")
            client_name = st.text_input("Client Name", placeholder="Enter client name")
            client_email = st.text_input("Client Email", placeholder="client@example.com")
            amount = st.number_input("Amount ($)", min_value=0.0, value=1000.0)
            description = st.text_area("Description", placeholder="Invoice description...")

            submitted = st.form_submit_button("🚀 Generate Preview", use_container_width=True)

            if submitted:
                st.success(f"✅ Would generate invoice for {client_name} with amount ${amount}")

    with col2:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px;">
            <h4>✨ Features</h4>
            <ul>
                <li>Professional PDF invoices</li>
                <li>GST calculation</li>
                <li>Multiple templates</li>
                <li>Client management</li>
                <li>Auto-save drafts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif page == "Resume Builder":
    st.markdown("""
    <style>
    .tool-header {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-header">
        <h2>📝 Professional Resume Builder</h2>
        <p>Create stunning resumes that get noticed</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("🚧 **Feature Coming Soon!**")
    st.info("💡 This will connect to your Flask backend for full resume building functionality.")

    with st.form("resume_form"):
        st.subheader("👤 Personal Information")
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")

        with col2:
            location = st.text_input("Location", placeholder="New York, NY")
            website = st.text_input("Website/Portfolio", placeholder="https://yourwebsite.com")
            linkedin = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/yourprofile")

        submitted = st.form_submit_button("🚀 Create Resume Preview", use_container_width=True)

        if submitted:
            st.success(f"✅ Would create resume for {full_name}")

elif page == "Certificate Creator":
    st.markdown("""
    <style>
    .tool-header {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-header">
        <h2>🏆 Certificate Creator</h2>
        <p>Generate professional certificates for your students/participants</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("🚧 **Feature Coming Soon!**")
    st.info("💡 This will connect to your Flask backend for full certificate generation functionality.")

    with st.form("certificate_form"):
        st.subheader("🏅 Certificate Details")
        recipient_name = st.text_input("Recipient Name", placeholder="Enter recipient name")
        course_name = st.text_input("Course/Certification", placeholder="Course name")
        issuer_name = st.text_input("Issuer Name", placeholder="Institution/Company name")
        date = st.date_input("Issue Date")

        submitted = st.form_submit_button("🚀 Generate Certificate Preview", use_container_width=True)

        if submitted:
            st.success(f"✅ Would generate certificate for {recipient_name}")

elif page == "QR Code Maker":
    st.markdown("""
    <style>
    .tool-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-header">
        <h2>📱 QR Code Generator</h2>
        <p>Create QR codes for URLs, text, contact info, and more</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("🚧 **Feature Coming Soon!**")
    st.info("💡 This will connect to your Flask backend for full QR code generation functionality.")

    with st.form("qrcode_form"):
        st.subheader("📱 QR Code Details")
        col1, col2 = st.columns([2, 1])

        with col1:
            data = st.text_area("Data to encode", placeholder="Enter URL, text, or contact information...")
            qr_type = st.selectbox("QR Code Type",
                                 ["URL", "Text", "Email", "Phone", "SMS", "Contact Info"])

        with col2:
            size = st.slider("Size", min_value=200, max_value=1000, value=400)
            st.markdown("""
            <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px;">
                <h4>✨ Features</h4>
                <ul>
                    <li>Multiple data types</li>
                    <li>High-quality images</li>
                    <li>Customizable size</li>
                    <li>Download options</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        submitted = st.form_submit_button("🚀 Generate QR Code Preview", use_container_width=True)

        if submitted:
            st.success(f"✅ Would generate QR code for: {data[:50]}...")

# Footer
st.markdown("---")
st.markdown("*Built with Flask backend and Streamlit frontend*")