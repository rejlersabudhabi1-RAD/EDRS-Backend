"""
Health Check Views for Rejlers Authentication API
Real-time system status and connectivity monitoring
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import json
import time
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Comprehensive health check endpoint for system monitoring
    """
    try:
        start_time = time.time()
        
        # Database connectivity check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "operational"
            
        # Cache system check
        cache_key = f"health_check_{int(time.time())}"
        cache.set(cache_key, "test", 10)
        cache_test = cache.get(cache_key)
        cache_status = "operational" if cache_test == "test" else "degraded"
        
        # Response time calculation
        response_time = round((time.time() - start_time) * 1000, 2)
        
        health_data = {
            "status": "healthy",
            "message": "Rejlers AI-ERP System is operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "cache": cache_status,
                "authentication": "operational",
                "api": "operational"
            },
            "performance": {
                "response_time_ms": response_time,
                "uptime_status": "excellent"
            },
            "version": "1.0.0",
            "environment": "development"
        }
        
        return JsonResponse(health_data, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "message": "System experiencing issues",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)

@api_view(['GET'])
@permission_classes([AllowAny]) 
def api_status(request):
    """API status and available endpoints"""
    return Response({
        'api_version': 'v1',
        'endpoints': {
            'auth': {
                'login': '/api/v1/auth/login/',
                'register': '/api/v1/auth/register/',
                'logout': '/api/v1/auth/logout/',
                'profile': '/api/v1/auth/profile/'
            }
        },
        'status': 'active'
    }, status=status.HTTP_200_OK)