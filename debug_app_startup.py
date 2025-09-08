#!/usr/bin/env python3

import sys
import traceback
from flask import Flask
import sqlite3

# Add the current directory to the Python path
sys.path.insert(0, '.')

def test_app_startup():
    """Test if the app can start up without errors"""
    try:
        print("🔍 Testing app import...")
        from app import app
        print("✅ App imported successfully")
        
        print("\n🔍 Testing database connection...")
        conn = sqlite3.connect('nfl_fantasy.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025')
        count = cursor.fetchone()[0]
        print(f"✅ Database connected - {count} games found for Week 1")
        conn.close()
        
        print("\n🔍 Testing Flask app context...")
        with app.app_context():
            print("✅ Flask app context works")
            
        print("\n🔍 Testing template rendering...")
        with app.test_client() as client:
            # This will test if the template renders without errors
            response = client.get('/login')  # Test a simple page first
            print(f"✅ Login page status: {response.status_code}")
            
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def test_games_route():
    """Test the specific /games route"""
    try:
        print("\n🔍 Testing /games route specifically...")
        from app import app
        
        with app.test_client() as client:
            # Create a test session to simulate being logged in
            with client.session_transaction() as sess:
                sess['user_id'] = 1  # Assume user ID 1 exists
                sess['username'] = 'test_user'
                sess['is_admin'] = False
            
            response = client.get('/games')
            print(f"Games route status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ /games route works!")
                # Check if the response contains expected content
                data = response.get_data(as_text=True)
                if 'Make Your Picks' in data:
                    print("✅ Page title found in response")
                if 'current-score' in data:
                    print("✅ Score elements found in response")
                else:
                    print("⚠️  No score elements found in response")
            else:
                print(f"❌ /games route returned status {response.status_code}")
                print("Response headers:", dict(response.headers))
                
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ Error testing /games route:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏈 NFL Fantasy App Debug Test")
    print("=" * 50)
    
    if test_app_startup():
        test_games_route()
    else:
        print("\n❌ Basic app startup failed - cannot test /games route")
