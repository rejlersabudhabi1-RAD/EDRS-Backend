from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('login/', views.RejlersLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='profile_detail'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Password reset
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),
    
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]