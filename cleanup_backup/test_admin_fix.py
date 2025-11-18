#!/usr/bin/env python3
"""
Test script to verify admin functionality after removing debug routes
"""

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_admin_routes():
    """Test admin routes to ensure they work properly"""
    
    base_url = "http://localhost"
    session = requests.Session()
    
    print("🔍 Testing Admin Interface Fix")
    print("=" * 50)
    
    # Test 1: Login as admin (assuming you have admin credentials)
    print("1. Testing admin login...")
    login_data = {
        'username': 'admin',  # Replace with actual admin username
        'password': 'admin123'  # Replace with actual admin password
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data, verify=False)
    
    if "Admin Panel" in login_response.text or login_response.url.endswith('/admin'):
        print("   ✅ Admin login successful")
    else:
        print("   ❌ Admin login failed")
        print(f"   Response URL: {login_response.url}")
        return
    
    # Test 2: Access admin panel
    print("2. Testing admin panel access...")
    admin_response = session.get(f"{base_url}/admin", verify=False)
    
    if admin_response.status_code == 200 and "League Administration" in admin_response.text:
        print("   ✅ Admin panel accessible")
    else:
        print(f"   ❌ Admin panel failed (Status: {admin_response.status_code})")
        return
    
    # Test 3: Test admin/all_picks route (should return JSON, not debug text)
    print("3. Testing admin all_picks route...")
    picks_response = session.get(f"{base_url}/admin/all_picks?week=1&year=2025", verify=False)
    
    if picks_response.status_code == 200:
        try:
            # Try to parse as JSON
            picks_data = picks_response.json()
            print(f"   ✅ Admin all_picks working - {len(picks_data)} picks found")
            
            # Check if it's not debug data
            if isinstance(picks_data, list):
                print("   ✅ Response is proper JSON list (not debug text)")
            else:
                print(f"   ⚠️  Response type: {type(picks_data)}")
                
        except json.JSONDecodeError:
            print("   ❌ Response is not valid JSON:")
            print(f"   Response text (first 200 chars): {picks_response.text[:200]}")
            if "DEBUG:" in picks_response.text:
                print("   🚨 Still contains DEBUG content - fix not complete!")
    else:
        print(f"   ❌ Admin all_picks failed (Status: {picks_response.status_code})")
    
    # Test 4: Test admin/simple_picks route
    print("4. Testing admin simple_picks route...")
    simple_picks_response = session.get(f"{base_url}/admin/simple_picks?week=1&year=2025", verify=False)
    
    if simple_picks_response.status_code == 200:
        try:
            simple_picks_data = simple_picks_response.json()
            print(f"   ✅ Admin simple_picks working - {len(simple_picks_data)} picks found")
        except json.JSONDecodeError:
            print("   ❌ Simple picks response is not valid JSON")
            print(f"   Response text (first 200 chars): {simple_picks_response.text[:200]}")
    else:
        print(f"   ❌ Admin simple_picks failed (Status: {simple_picks_response.status_code})")
    
    print("\n✅ Admin interface testing complete!")
    
    # Test 5: Session persistence
    print("5. Testing session persistence (refresh admin page)...")
    admin_refresh = session.get(f"{base_url}/admin", verify=False)
    
    if admin_refresh.status_code == 200 and "League Administration" in admin_refresh.text:
        print("   ✅ Session persists after refresh")
    else:
        print("   ❌ Session lost after refresh")

if __name__ == "__main__":
    try:
        test_admin_routes()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
