"""
Test views for session debugging
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import get_user_model
import logging

log = logging.getLogger(__name__)


@ensure_csrf_cookie
def session_debug(request):
    """
    Debug endpoint to check session status
    """
    session_info = {
        'session_key': request.session.session_key,
        'session_modified': request.session.modified,
        'session_accessed': request.session.accessed,
        'user_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'username': request.user.username if request.user.is_authenticated else None,
        'cookies': dict(request.COOKIES),
        'session_data': dict(request.session),
    }
    
    log.info(f"Session debug info: {session_info}")
    
    return JsonResponse(session_info)


@login_required
@ensure_csrf_cookie
def protected_test(request):
    """
    Test endpoint that requires authentication
    """
    return JsonResponse({
        'status': 'success',
        'message': 'Authentication working!',
        'user': request.user.username,
        'user_id': request.user.id,
        'session_key': request.session.session_key,
    })



























































