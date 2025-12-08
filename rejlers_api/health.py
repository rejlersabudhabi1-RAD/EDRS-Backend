"""
Health check views for Railway deployment
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.core.cache import cache
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint for Railway - Basic version without DB dependency
    """
    # Basic health check that always returns 200 for Railway startup
    health_data = {
        "status": "healthy",
        "message": "Rejlers EDRS Backend is running",
        "application": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-12-08T00:00:00Z"
    }
    
    return JsonResponse(health_data, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def detailed_health_check(request):
    """
    Detailed health check with database and cache checks
    """
    try:
        # Check database connection
        db_conn = connections['default']
        db_conn.cursor()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check cache (if Redis is configured)
    try:
        cache.set('health_check', 'test', 10)
        cache_result = cache.get('health_check')
        cache_status = "healthy" if cache_result == 'test' else "unhealthy"
    except Exception as e:
        cache_status = f"unavailable: {str(e)}"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": "2024-12-08T00:00:00Z",
        "services": {
            "database": db_status,
            "cache": cache_status,
            "application": "healthy"
        },
        "version": "1.0.0"
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JsonResponse(health_data, status=status_code)

@csrf_exempt  
@require_http_methods(["GET"])
def ready_check(request):
    """
    Readiness probe for Railway
    """
    return JsonResponse({
        "status": "ready",
        "message": "Rejlers EDRS Backend is ready to serve requests"
    })