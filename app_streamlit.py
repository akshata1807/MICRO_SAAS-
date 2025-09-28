import streamlit as st
import requests
import json

# Streamlit Cloud expects a Streamlit app, not a Flask app
# This wrapper provides a Streamlit interface to our Flask backend

st.set_page_config(
    page_title="Micro SaaS Platform",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Micro SaaS Platform")
st.subheader("Flask Backend with Streamlit Frontend")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Invoice Generator", "Resume Builder", "Certificate Creator", "QR Code Maker"]
)

# Main content based on selected page
if page == "Home":
    st.write("""
    ## Welcome to Micro SaaS Platform! 🎉

    This is a comprehensive SaaS platform that provides:

    - **📄 Invoice Generator** - Create professional invoices with GST support
    - **📝 Resume Builder** - Build and customize professional resumes
    - **🏆 Certificate Creator** - Generate certificates with customizable templates
    - **📱 QR Code Maker** - Create QR codes for various data types

    ### Features:
    - ✅ User Authentication & Registration
    - ✅ Subscription Management
    - ✅ Admin Panel
    - ✅ Analytics Dashboard
    - ✅ Bulk Operations
    - ✅ Email Notifications
    - ✅ File Upload Support

    **Note**: This Streamlit app serves as a frontend to our Flask backend running on port 5000.
    """)

    # Health check for Flask backend
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Flask backend is running and healthy!")
        else:
            st.warning(f"⚠️ Flask backend returned status: {response.status_code}")
    except:
        st.info("ℹ️ Flask backend health check - connect to localhost:5000")

elif page == "Invoice Generator":
    st.header("📄 Invoice Generator")
    st.write("Invoice generation features will be available here.")

    with st.form("invoice_form"):
        st.subheader("Create New Invoice")
        client_name = st.text_input("Client Name")
        amount = st.number_input("Amount", min_value=0.0)
        submitted = st.form_submit_button("Generate Invoice")

        if submitted:
            st.info(f"Would generate invoice for {client_name} with amount ${amount}")

elif page == "Resume Builder":
    st.header("📝 Resume Builder")
    st.write("Resume building features will be available here.")

    with st.form("resume_form"):
        st.subheader("Create New Resume")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Create Resume")

        if submitted:
            st.info(f"Would create resume for {full_name}")

elif page == "Certificate Creator":
    st.header("🏆 Certificate Creator")
    st.write("Certificate creation features will be available here.")

    with st.form("certificate_form"):
        st.subheader("Create New Certificate")
        recipient_name = st.text_input("Recipient Name")
        course_name = st.text_input("Course/Certification Name")
        submitted = st.form_submit_button("Generate Certificate")

        if submitted:
            st.info(f"Would generate certificate for {recipient_name}")

elif page == "QR Code Maker":
    st.header("📱 QR Code Maker")
    st.write("QR code generation features will be available here.")

    with st.form("qrcode_form"):
        st.subheader("Create New QR Code")
        data = st.text_input("Data to encode")
        submitted = st.form_submit_button("Generate QR Code")

        if submitted:
            st.info(f"Would generate QR code for: {data}")

# Footer
st.markdown("---")
st.markdown("*Built with Flask backend and Streamlit frontend*")