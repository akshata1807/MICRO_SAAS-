#!/usr/bin/env python3
"""
Script to view all data in the SQLite database
"""
from app import create_app, db
from app.models import User, AdminUser, Invoice, QRCode, Subscription, Resume, Certificate, Template
import os

def view_table_data(model_class, table_name):
    """View data from a specific table"""
    try:
        records = model_class.query.all()
        if not records:
            print(f"\n{table_name} table is empty.")
            return

        print(f"\n{table_name} table ({len(records)} records):")
        print("-" * 80)

        # Get column names from the model
        columns = [column.name for column in model_class.__table__.columns]

        # Print header
        header = " | ".join(f"{col:<15}" for col in columns)
        print(header)
        print("-" * len(header))

        # Print records
        for record in records:
            row = []
            for col in columns:
                value = getattr(record, col)
                if value is None:
                    value = "NULL"
                elif hasattr(value, 'strftime'):  # datetime objects
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    value = str(value)[:15]  # truncate long strings
                row.append(f"{value:<15}")
            print(" | ".join(row))

    except Exception as e:
        print(f"Error viewing {table_name}: {e}")

def main():
    """Main function to view all database data"""
    app = create_app()

    with app.app_context():
        print("=== DATABASE CONTENTS ===")
        print(f"Database file: {os.path.abspath('site.db')}")

        # View all tables
        tables = [
            (User, "User"),
            (AdminUser, "AdminUser"),
            (Invoice, "Invoice"),
            (QRCode, "QRCode"),
            (Subscription, "Subscription"),
            (Resume, "Resume"),
            (Certificate, "Certificate"),
            (Template, "Template")
        ]

        for model_class, table_name in tables:
            view_table_data(model_class, table_name)

        print("\n=== END OF DATABASE CONTENTS ===")

if __name__ == "__main__":
    main()