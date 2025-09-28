"""
Streamlit Cloud Deployment Setup Script
Run this locally to test if your app will work on Streamlit Cloud
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'sqlalchemy',
        'jinja2',
        'werkzeug'
    ]

    failed_packages = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_packages.append(package)

    return failed_packages

def main():
    print("🔍 Testing Streamlit Cloud compatibility...")
    print(f"Python version: {sys.version}")
    print()

    failed = test_imports()

    if not failed:
        print("\n✅ All packages imported successfully!")
        print("Your app should work on Streamlit Cloud.")
    else:
        print(f"\n❌ {len(failed)} packages failed to import.")
        print("Please check your requirements.txt file.")

if __name__ == "__main__":
    main()