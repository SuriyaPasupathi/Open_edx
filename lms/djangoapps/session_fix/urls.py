"""
URLs for session debugging
"""

from django.urls import path
from . import views

urlpatterns = [
    path('session-debug/', views.session_debug, name='session_debug'),
    path('protected-test/', views.protected_test, name='protected_test'),
]



























































