"""
Authentication API URLs for Rejlers AI-Powered ERP System
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views, health_views

app_name = 'auth_api'

urlpatterns = [
    # Health endpoints
    path('health/', health_views.health_check, name='health_check'),
    path('status/', health_views.api_status, name='api_status'),
    
    # Authentication endpoints
    path('login/', api_views.CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', api_views.register_user, name='register'),
    path('logout/', api_views.logout_user, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('profile/', api_views.user_profile, name='user_profile'),
    
    # Utility endpoints
    path('roles/', api_views.get_roles, name='get_roles'),
]