"""
Minimal URLs for Railway deployment
"""
from django.urls import path
from simple_health import health_check, ready_check

urlpatterns = [
    # Health checks - multiple endpoints for Railway to find
    path('', health_check, name='root'),
    path('health/', health_check, name='health'),
    path('api/v1/health/', health_check, name='api_health'),
    path('api/v1/ready/', ready_check, name='ready'),
    path('ping/', health_check, name='ping'),
]