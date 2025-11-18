#!/usr/bin/env python3
"""
Debug script to test the /games route and find the error
"""

import requests
import sys

def test_games_route():
    """Test the /games route to see what error occurs"""
    
    try:
        print("🔍 Testing /games route...")
        
        # Test without session first
        response = requests.get('http://localhost:5000/games', allow_redirects=False)
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Correctly redirects to login (expected for non-authenticated user)")
            location = response.headers.get('Location', 'No location header')
            print(f"   Redirect to: {location}")
        elif response.status_code == 500:
            print("❌ Internal Server Error (500)")
            print(f"   Response text: {response.text[:500]}...")
        else:
            print(f"   Response text: {response.text[:200]}...")
            
        # Test the login page to make sure basic routing works
        print("\n🔍 Testing /login route...")
        login_response = requests.get('http://localhost:5000/login')
        print(f"📋 Login response status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Login page also has issues")
            print(f"   Response text: {login_response.text[:200]}...")
        else:
            print("✅ Login page works fine")
            
        # Test the index page
        print("\n🔍 Testing / (index) route...")
        index_response = requests.get('http://localhost:5000/', allow_redirects=False)
        print(f"📋 Index response status: {index_response.status_code}")
        
        if index_response.status_code == 500:
            print("❌ Index page has 500 error too")
            print(f"   Response text: {index_response.text[:500]}...")
        else:
            print("✅ Index page works or redirects properly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🏈 La Casa de Todos - Route Debug Tool")
    print("=" * 50)
    test_games_route()
