""" URLs configuration for the health api."""

from django.urls import path

from lms.djangoapps.health_api.views import HealthAPIView

app_name = 'health_api'
urlpatterns = [
    path('', HealthAPIView.as_view(), name='health'),
]


