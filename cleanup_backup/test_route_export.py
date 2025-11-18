#!/usr/bin/env python3

# Test the exact export route as a web request
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_export_route():
    """Test the actual export route via Flask test client"""
    
    with app.test_client() as client:
        print("✅ Flask test client created")
        
        # First, we need to login to get a session
        with client.session_transaction() as sess:
            # Manually set session data
            sess['user_id'] = 1
            sess['username'] = 'test_user'
            sess['is_admin'] = False
        
        print("✅ Session data set")
        
        # Test the export route with parameters
        response = client.get('/export_my_picks_csv?week=1&year=2025')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Export route successful")
            print(f"Content-Type: {response.content_type}")
            print(f"Response length: {len(response.data)} bytes")
            
            # Check if it's CSV content
            if 'text/csv' in response.content_type:
                csv_content = response.data.decode('utf-8')
                print(f"CSV preview (first 200 chars):\n{csv_content[:200]}...")
                return True
            else:
                print(f"Unexpected content type: {response.content_type}")
                if response.data:
                    print(f"Response data: {response.data.decode('utf-8')[:500]}...")
                return False
        
        elif response.status_code == 500:
            print("❌ Internal server error (500)")
            if response.data:
                error_content = response.data.decode('utf-8')
                print(f"Error response: {error_content}")
            return False
        
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            if response.data:
                print(f"Response: {response.data.decode('utf-8')}")
            return False

def test_export_route_display_format():
    """Test the export route with display format"""
    
    with app.test_client() as client:
        print("\n--- Testing display format ---")
        
        # Set session data
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test_user'
            sess['is_admin'] = False
        
        # Test the export route with display format
        response = client.get('/export_my_picks_csv?week=1&year=2025&display_format=true')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Export route with display format successful")
            print(f"Content-Type: {response.content_type}")
            
            if 'text/html' in response.content_type:
                html_content = response.data.decode('utf-8')
                print(f"HTML preview (first 300 chars):\n{html_content[:300]}...")
                return True
            else:
                print(f"Unexpected content type: {response.content_type}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            if response.data:
                print(f"Response: {response.data.decode('utf-8')[:500]}...")
            return False

if __name__ == "__main__":
    print("Testing CSV export route...")
    success1 = test_export_route()
    
    print("\nTesting display format export route...")
    success2 = test_export_route_display_format()
    
    overall_success = success1 and success2
    print(f"\nOverall test result: {'PASSED' if overall_success else 'FAILED'}")
