#!/usr/bin/env python3
"""
Test script to verify admin interface starts with current week
"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_admin_current_week():
    """Test that admin interface starts with current week"""
    
    base_url = "http://localhost"
    
    print("🔍 Testing Admin Interface Current Week Fix")
    print("=" * 50)
    
    # Test admin page loads and contains current week selection
    print("1. Testing admin page loads with current week...")
    
    try:
        admin_response = requests.get(f"{base_url}/admin", verify=False)
        
        if admin_response.status_code == 200:
            # Check if it contains the current week selection
            if 'option value="2" selected' in admin_response.text:
                print("   ✅ Admin page loads with Week 2 selected (current week)")
            elif 'option value="1" selected' in admin_response.text:
                print("   ❌ Admin page still shows Week 1 selected (old behavior)")
            else:
                print("   ⚠️  Week selection not found in admin page")
            
            # Check if JavaScript initializes with correct week
            if 'let currentWeek = 2;' in admin_response.text:
                print("   ✅ JavaScript initializes with Week 2 (current week)")
            elif 'let currentWeek = 1;' in admin_response.text:
                print("   ❌ JavaScript still initializes with Week 1 (old behavior)")
            else:
                print("   ⚠️  JavaScript currentWeek initialization not found")
                
        else:
            print(f"   ❌ Admin page failed to load (Status: {admin_response.status_code})")
            
    except Exception as e:
        print(f"   ❌ Error testing admin page: {e}")
    
    print("\n✅ Admin current week testing complete!")

if __name__ == "__main__":
    try:
        test_admin_current_week()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
