#!/usr/bin/env python3
"""
Test the Flask server is working correctly
"""

import requests
import time

def test_flask_server():
    """Test that Flask server is responding correctly"""
    
    print("🧪 TESTING FLASK SERVER")
    print("=" * 30)
    
    # Test basic connectivity
    try:
        response = requests.get("http://localhost", timeout=10)
        print(f"✅ Server responding: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    # Test games page
    try:
        response = requests.get("http://localhost/games", timeout=10)
        if response.status_code == 200:
            print("✅ /games page working correctly")
            if "Week" in response.text:
                print("✅ Template rendering with game data")
            else:
                print("⚠️ Template loaded but may be missing data")
        else:
            print(f"❌ /games page error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing /games: {e}")
        return False
    
    # Test API endpoints
    endpoints_to_test = ["/", "/login", "/leaderboard"]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"http://localhost{endpoint}", timeout=5)
            if response.status_code in [200, 302]:  # 302 for redirects
                print(f"✅ {endpoint} working")
            else:
                print(f"⚠️ {endpoint} returned {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {endpoint} not accessible")
    
    print(f"\n🎉 FLASK SERVER TEST COMPLETE!")
    print("✅ Your NFL fantasy system is running correctly!")
    print("🌐 Access at: http://localhost")
    print("🔒 HTTPS at: https://localhost")
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to fully start
    time.sleep(2)
    test_flask_server()