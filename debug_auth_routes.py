#!/usr/bin/env python3
"""
Debug script to test authenticated routes
"""

import requests
import sys

def test_authenticated_routes():
    """Test routes with authentication"""
    
    session = requests.Session()
    
    try:
        print("🔍 Testing authenticated access...")
        
        # First, try to login
        print("1. Getting login page...")
        login_page = session.get('http://localhost:5000/login')
        if login_page.status_code != 200:
            print(f"❌ Cannot get login page: {login_page.status_code}")
            return
            
        # Try to access games page directly (should redirect to login)
        print("2. Testing /games without auth...")
        games_response = session.get('http://localhost:5000/games', allow_redirects=False)
        print(f"   Status: {games_response.status_code}")
        
        if games_response.status_code == 500:
            print("❌ /games route returns 500 error")
            print("   This indicates an internal server error in the games() function")
            print(f"   Response: {games_response.text[:500]}")
        else:
            print(f"✅ /games redirects properly (status {games_response.status_code})")
            
        # Test other routes that might be causing issues
        print("3. Testing /index without auth...")
        index_response = session.get('http://localhost:5000/', allow_redirects=False)
        print(f"   Status: {index_response.status_code}")
        
        if index_response.status_code == 500:
            print("❌ Index route also returns 500 error")
            print(f"   Response: {index_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🏈 La Casa de Todos - Authenticated Route Debug")
    print("=" * 50)
    test_authenticated_routes()
