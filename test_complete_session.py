#!/usr/bin/env python3
"""
Complete session test for Open edX
"""

import requests
import json
import time
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:18000"
LOGIN_URL = f"{BASE_URL}/api/user/v1/account/login_session/"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
SESSION_DEBUG_URL = f"{BASE_URL}/debug/session-debug/"
PROTECTED_TEST_URL = f"{BASE_URL}/debug/protected-test/"

def test_complete_session_flow():
    """Test the complete session flow with debugging"""
    print("🔍 Complete Open edX Session Test")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Check initial session status
    print("1. Checking initial session status...")
    try:
        response = session.get(SESSION_DEBUG_URL)
        if response.status_code == 200:
            session_info = response.json()
            print(f"Initial session: {json.dumps(session_info, indent=2)}")
        else:
            print(f"❌ Failed to get session debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting session debug: {e}")
    
    # Step 2: Get CSRF token
    print("\n2. Getting CSRF token...")
    try:
        response = session.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token not found")
                return
        else:
            print(f"❌ Failed to get login page: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting CSRF token: {e}")
        return
    
    # Step 3: Login
    print("\n3. Attempting login...")
    login_data = {
        'email': 'murugadass@gmail.com',
        'password': 'ChangeMe!2345',
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': f"{BASE_URL}/login"
    }
    
    try:
        response = session.post(LOGIN_URL, data=login_data, headers=headers)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                login_result = response.json()
                print(f"Login response: {json.dumps(login_result, indent=2)}")
                
                if login_result.get('success'):
                    print("✅ Login successful!")
                    print(f"Redirect URL: {login_result.get('redirect_url')}")
                else:
                    print("❌ Login failed")
                    return
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
                return
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 4: Check session after login
    print("\n4. Checking session after login...")
    try:
        response = session.get(SESSION_DEBUG_URL)
        if response.status_code == 200:
            session_info = response.json()
            print(f"Session after login: {json.dumps(session_info, indent=2)}")
            
            if session_info.get('user_authenticated'):
                print("✅ User is authenticated!")
            else:
                print("❌ User is not authenticated")
        else:
            print(f"❌ Failed to get session debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking session: {e}")
    
    # Step 5: Test protected endpoint
    print("\n5. Testing protected endpoint...")
    try:
        response = session.get(PROTECTED_TEST_URL)
        print(f"Protected endpoint response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Protected endpoint response: {json.dumps(result, indent=2)}")
                print("✅ Protected endpoint accessible!")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
        elif response.status_code == 302:
            print("❌ Protected endpoint redirected (likely to login)")
        else:
            print(f"❌ Protected endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Protected endpoint test error: {e}")
    
    # Step 6: Test dashboard access
    print("\n6. Testing dashboard access...")
    try:
        response = session.get(DASHBOARD_URL)
        print(f"Dashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard accessible!")
            if 'dashboard' in response.text.lower() or 'my courses' in response.text.lower():
                print("✅ Dashboard content loaded successfully!")
            else:
                print("⚠️ Dashboard response unclear")
        elif response.status_code == 302:
            print("❌ Dashboard redirected (likely to login)")
            print(f"Redirect location: {response.headers.get('Location')}")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
    
    # Step 7: Final session check
    print("\n7. Final session check...")
    try:
        response = session.get(SESSION_DEBUG_URL)
        if response.status_code == 200:
            session_info = response.json()
            print(f"Final session: {json.dumps(session_info, indent=2)}")
        else:
            print(f"❌ Failed to get final session debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final session debug: {e}")

if __name__ == "__main__":
    test_complete_session_flow()



























































