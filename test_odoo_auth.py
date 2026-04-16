#!/usr/bin/env python3
"""Test Odoo XML-RPC authentication"""
import xmlrpc.client
from dotenv import load_dotenv
import os

load_dotenv()

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'ai_employee')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin123')

print(f"Testing Odoo authentication...")
print(f"  URL: {ODOO_URL}")
print(f"  DB: {ODOO_DB}")
print(f"  Username: {ODOO_USERNAME}")
print(f"  Password: {ODOO_PASSWORD}")

# Test common endpoint
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')

# Get version info
version = common.version()
print(f"\nOdoo version info: {version}")

# Try authentication
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
print(f"Authentication result: uid={uid}")

if uid:
    print("\nSUCCESS! Authentication worked.")
    # Try to get partner info
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    partner = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_read',
        [[('email', 'ilike', 'admin')]],
        {'fields': ['id', 'name', 'email'], 'limit': 1}
    )
    print(f"Admin partner: {partner}")
else:
    print("\nFAILED! Authentication did not work.")
    print("Try checking your admin username/password in Odoo.")
