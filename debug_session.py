#!/usr/bin/env python3
"""
Debug script to test Open edX session handling
"""

import requests
import json
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:18000"
LOGIN_URL = f"{BASE_URL}/api/user/v1/account/login_session/"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
SESSION_API_URL = f"{BASE_URL}/api/user/v1/account/"

def test_session_flow():
    """Test the complete session flow"""
    print("🔍 Testing Open edX Session Flow")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Get CSRF token
    print("1. Getting CSRF token...")
    try:
        response = session.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            # Extract CSRF token from HTML
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
    
    # Step 2: Login
    print("\n2. Attempting login...")
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
    
    # Step 3: Check session cookies
    print("\n3. Checking session cookies...")
    cookies = session.cookies.get_dict()
    print(f"Cookies: {cookies}")
    
    if 'sessionid' in cookies:
        print("✅ Session cookie found")
        print(f"Session ID: {cookies['sessionid'][:20]}...")
    else:
        print("❌ No session cookie found")
        return
    
    # Step 4: Test dashboard access
    print("\n4. Testing dashboard access...")
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
    
    # Step 5: Test session API
    print("\n5. Testing session API...")
    try:
        response = session.get(SESSION_API_URL)
        print(f"Session API response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                user_data = response.json()
                print(f"User data: {json.dumps(user_data, indent=2)}")
                
                if user_data.get('username'):
                    print(f"✅ User authenticated: {user_data.get('username')}")
                else:
                    print("❌ User not authenticated")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
        else:
            print(f"❌ Session API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Session API test error: {e}")

if __name__ == "__main__":
    test_session_flow()



























































