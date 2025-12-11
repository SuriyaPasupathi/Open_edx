"""
Health API Views for checking the health status of the application.
"""

import logging
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

log = logging.getLogger(__name__)


class HealthAPIView(APIView):
    """
    Provides an API endpoint to check the health status of the application.
    
    Returns a JSON response with the health status and timestamp.
    """

    def get(self, request):
        """
        Return the health status of the application.
        
        **GET Response Values**
        ```
        {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00Z",
            "service": "lms"
        }
        ```
        """
        try:
            response_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "lms"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:  # lint-amnesty, pylint: disable=broad-except
            log.error('Health check failed: %s', str(e))
            response_data = {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "lms",
                "error": str(e)
            }
            return Response(response_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)


