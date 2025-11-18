#!/usr/bin/env python3
"""
Server Health Diagnostic Script
Tests various aspects of the web application to diagnose issues
"""

import requests
import sys
import time

def test_server_health(base_url="http://localhost:5000"):
    """Test server health and functionality"""
    print("🏈 La Casa de Todos - Server Health Check")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", f"{base_url}/health"),
        ("Root Page", f"{base_url}/"),
        ("Login Page", f"{base_url}/login"),
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            print(f"Testing {test_name}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {test_name}: OK (200)")
                results.append(True)
            elif response.status_code == 302:
                print(f"  ✅ {test_name}: Redirect (302) - Expected")
                results.append(True)
            else:
                print(f"  ⚠️  {test_name}: Status {response.status_code}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {test_name}: Connection refused - Server may be down")
            results.append(False)
        except requests.exceptions.Timeout:
            print(f"  ❌ {test_name}: Timeout - Server not responding")
            results.append(False)
        except Exception as e:
            print(f"  ❌ {test_name}: Error - {e}")
            results.append(False)
    
    # Test POST to root (should not give 405 anymore)
    try:
        print("Testing POST to root (should not get 405)...")
        response = requests.post(f"{base_url}/", timeout=10)
        if response.status_code == 302:
            print("  ✅ POST /: Redirect (302) - Fixed!")
            results.append(True)
        elif response.status_code == 405:
            print("  ❌ POST /: Still getting 405 Method Not Allowed")
            results.append(False)
        else:
            print(f"  ⚠️  POST /: Status {response.status_code}")
            results.append(True)  # Not 405, so improvement
    except Exception as e:
        print(f"  ❌ POST /: Error - {e}")
        results.append(False)
    
    # Test security blocking
    try:
        print("Testing security blocking (.env request)...")
        response = requests.get(f"{base_url}/.env", timeout=10)
        if response.status_code == 404:
            print("  ✅ Security: .env blocked with 404")
            results.append(True)
        else:
            print(f"  ⚠️  Security: .env returned {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"  ❌ Security test: Error - {e}")
        results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("Server appears to be healthy!")
    elif passed >= total * 0.8:
        print(f"⚠️  MOSTLY WORKING ({passed}/{total})")
        print("Server is functional but may have minor issues")
    else:
        print(f"❌ MULTIPLE ISSUES ({passed}/{total})")
        print("Server needs attention")
    
    return passed == total

if __name__ == "__main__":
    # Test localhost by default, or use provided URL
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"Testing server at: {url}")
    print()
    
    success = test_server_health(url)
    sys.exit(0 if success else 1)
