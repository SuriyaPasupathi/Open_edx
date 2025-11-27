"""
Custom middleware to fix session cookie issues
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

log = logging.getLogger(__name__)


class SessionCookieFixMiddleware(MiddlewareMixin):
    """
    Middleware to fix session cookie issues by ensuring proper cookie settings
    """
    
    def process_response(self, request, response):
        """
        Fix session cookie settings to ensure they work properly
        """
        # Only process if we have a session
        if hasattr(request, 'session') and request.session.session_key:
            # Get the session cookie name
            session_cookie_name = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
            
            # Check if session cookie is being set
            if session_cookie_name in response.cookies:
                session_cookie = response.cookies[session_cookie_name]
                
                # Log session cookie details for debugging
                log.debug(f"Session cookie being set: {session_cookie_name}")
                log.debug(f"Session cookie value: {session_cookie.value[:20]}...")
                log.debug(f"Session cookie domain: {session_cookie.get('domain', 'None')}")
                log.debug(f"Session cookie path: {session_cookie.get('path', 'None')}")
                log.debug(f"Session cookie secure: {session_cookie.get('secure', 'None')}")
                log.debug(f"Session cookie httponly: {session_cookie.get('httponly', 'None')}")
                log.debug(f"Session cookie samesite: {session_cookie.get('samesite', 'None')}")
                
                # Ensure proper cookie settings for development
                session_cookie['domain'] = None  # No domain restriction
                session_cookie['path'] = '/'  # Available for all paths
                session_cookie['secure'] = False  # Allow HTTP for development
                session_cookie['httponly'] = False  # Allow JavaScript access for debugging
                session_cookie['samesite'] = 'Lax'  # Allow cross-site requests
                
                log.debug("Session cookie settings fixed for development")
            else:
                log.warning("Session cookie not found in response")
        
        return response



























































