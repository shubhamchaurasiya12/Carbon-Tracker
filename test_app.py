#!/usr/bin/env python3
"""
Simple test script to verify the Carbon Tracker application
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        print("✓ All Flask modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test if the Flask app can be created"""
    try:
        # Import the app
        from app import app, db
        
        # Test database creation
        with app.app_context():
            db.create_all()
            print("✓ Flask app created and database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_templates():
    """Test if all required templates exist"""
    required_templates = [
        'base.html',
        'login.html', 
        'register.html',
        'dashboard.html',
        'admin.html'
    ]
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print(f"✗ Templates directory '{templates_dir}' not found")
        return False
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
    
    if missing_templates:
        print(f"✗ Missing templates: {missing_templates}")
        return False
    else:
        print("✓ All required templates found")
        return True

def main():
    """Run all tests"""
    print("Testing Carbon Tracker Application...")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Template Files", test_templates)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the app: python app.py")
        print("3. Open browser: http://localhost:5000")
        print("\nDefault admin login:")
        print("Email: admin@carbon.com")
        print("Password: admin123")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 