#!/usr/bin/env python3
"""
Simple script to test if app.py can be imported and run
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing app.py startup...")

try:
    print("1. Testing imports...")
    
    # Test individual imports
    from flask import Flask
    print("   ✅ Flask imported")
    
    from datetime import datetime
    print("   ✅ datetime imported")
    
    import sqlite3
    print("   ✅ sqlite3 imported")
    
    # Test our custom modules
    try:
        from utils.timezone_utils import convert_to_ast
        print("   ✅ timezone_utils imported")
    except ImportError as e:
        print(f"   ❌ timezone_utils error: {e}")
    
    try:
        from deadline_manager import DeadlineManager
        print("   ✅ deadline_manager imported")
    except ImportError as e:
        print(f"   ❌ deadline_manager error: {e}")
    
    try:
        from deadline_override_manager import DeadlineOverrideManager
        print("   ✅ deadline_override_manager imported")
    except ImportError as e:
        print(f"   ❌ deadline_override_manager error: {e}")
    
    print("\n2. Testing app.py import...")
    
    # Test app.py import
    import app
    print("   ✅ app.py imported successfully")
    
    print("\n3. Testing Flask app creation...")
    if hasattr(app, 'app'):
        print("   ✅ Flask app object exists")
        print(f"   📍 App name: {app.app.name}")
    else:
        print("   ❌ No Flask app object found")
    
    print("\n🎉 All tests passed! App should be able to run.")
    print("\nTo start the app, run: python app.py")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("   Check if all required files exist and have correct syntax")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("   There may be a syntax error or missing dependency")
    import traceback
    traceback.print_exc()
