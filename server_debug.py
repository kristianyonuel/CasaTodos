#!/usr/bin/env python3
"""
Comprehensive debug script for La Casa de Todos server issues
Run this on your remote server to diagnose the "Make Picks" error
"""

import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False
        
    try:
        import sqlite3
        print("✅ SQLite3: Available")
    except ImportError as e:
        print(f"❌ SQLite3 import error: {e}")
        return False
        
    try:
        from deadline_manager import DeadlineManager
        print("✅ DeadlineManager: Available")
    except ImportError as e:
        print(f"❌ DeadlineManager import error: {e}")
        print("   This might be the issue!")
        return False
        
    try:
        from utils.timezone_utils import convert_to_ast, format_ast_time
        print("✅ Timezone utils: Available")
    except ImportError as e:
        print(f"❌ Timezone utils import error: {e}")
        print("   This might be the issue!")
        return False
        
    try:
        from api_rate_limiter import check_api_rate_limit, get_api_calls_remaining
        print("✅ API rate limiter: Available")
    except ImportError as e:
        print(f"❌ API rate limiter import error: {e}")
        print("   This might be the issue!")
        return False
        
    return True

def test_database():
    """Test database connectivity and structure"""
    print("\n🔍 Testing database...")
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test basic tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'nfl_games', 'user_picks']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
            
        print(f"✅ Required tables present: {required_tables}")
        
        # Test games data
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025')
        game_count = cursor.fetchone()[0]
        print(f"✅ Games for week 1, 2025: {game_count}")
        
        # Test users
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"✅ Total users: {user_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🔍 Testing Flask app...")
    
    try:
        import app
        print("✅ App module imported successfully")
        
        # Check if routes are registered
        rules = []
        for rule in app.app.url_map.iter_rules():
            rules.append(str(rule))
            
        if '/games' in str(app.app.url_map):
            print("✅ /games route is registered")
        else:
            print("❌ /games route is NOT registered")
            print(f"   Available routes: {rules[:10]}...")  # Show first 10 routes
            
        return True
        
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        traceback.print_exc()
        return False

def test_specific_functions():
    """Test specific functions that might be failing"""
    print("\n🔍 Testing specific functions...")
    
    try:
        # Test datetime handling
        from datetime import datetime
        from utils.timezone_utils import convert_to_ast
        
        test_date = datetime.now()
        ast_date = convert_to_ast(test_date)
        print("✅ Datetime conversion works")
        
        # Test DeadlineManager
        from deadline_manager import DeadlineManager
        dm = DeadlineManager()
        deadline_data = dm.get_week_deadlines(1, 2025)
        print("✅ DeadlineManager.get_week_deadlines works")
        
        return True
        
    except Exception as e:
        print(f"❌ Function test error: {e}")
        traceback.print_exc()
        return False

def main():
    print("🏈 La Casa de Todos - Server Debug Tool")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Flask App", test_flask_app()))
    results.append(("Functions", test_specific_functions()))
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        
    if all(result[1] for result in results):
        print("\n🎯 All tests passed! The issue might be in the specific request context.")
        print("   Try accessing the app and check the server logs for the exact error.")
    else:
        print("\n🚨 Some tests failed! Fix these issues and the app should work.")

if __name__ == "__main__":
    main()
