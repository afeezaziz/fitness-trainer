#!/usr/bin/env python3
"""
Simple test to verify Flask app can start and templates are accessible
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app_simple import app
    print("✅ Flask app imported successfully")

    # Test template directory
    with app.test_client() as client:
        response = client.get('/')
        print(f"📄 Homepage status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Homepage loads successfully!")
        else:
            print(f"❌ Homepage error: {response.status_code}")

except Exception as e:
    print(f"❌ Error importing or running app: {e}")
    import traceback
    traceback.print_exc()