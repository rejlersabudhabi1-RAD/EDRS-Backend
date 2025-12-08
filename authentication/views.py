from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import RejlersUser, UserProfile, LoginHistory
from .serializers import (
    RejlersTokenObtainPairSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserProfileDetailSerializer,
    PasswordChangeSerializer, LoginHistorySerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)

logger = logging.getLogger('rejlers_api')


class RejlersLoginView(TokenObtainPairView):
    """
    Custom login view with JWT token generation
    """
    serializer_class = RejlersTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Log successful login
            user_email = request.data.get('email')
            try:
                user = RejlersUser.objects.get(email=user_email)
                LoginHistory.objects.create(
                    user=user,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    is_successful=True
                )
                
                # Update profile login count
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.login_count += 1
                profile.last_login_ip = self.get_client_ip(request)
                profile.save()
                
                logger.info(f"Successful login for user: {user_email}")
                
            except RejlersUser.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = RejlersUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"New user registered: {user.email}")
        
        return Response({
            'message': 'User registered successfully',
            'user_id': str(user.id),
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        logger.info(f"Profile updated for user: {request.user.email}")
        return response


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Detailed user profile with extended information
    """
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class PasswordChangeView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout user and blacklist refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Update logout time in login history
            try:
                last_login = LoginHistory.objects.filter(
                    user=request.user,
                    logout_time__isnull=True
                ).order_by('-login_time').first()
                
                if last_login:
                    last_login.logout_time = timezone.now()
                    last_login.save()
            except Exception as e:
                logger.warning(f"Could not update logout time: {e}")
            
            logout(request)
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)


class LoginHistoryView(generics.ListAPIView):
    """
    View user login history
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)[:10]


class PasswordResetRequestView(APIView):
    """
    Request password reset
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = RejlersUser.objects.get(email=email)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            
            # In production, send email with reset link
            # For now, return the token (development only)
            logger.info(f"Password reset requested for: {email}")
            
            return Response({
                'message': 'Password reset instructions sent to email',
                'reset_token': token,  # Remove this in production
                'user_id': str(user.id)  # Remove this in production
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    List all users (admin only)
    """
    queryset = RejlersUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        office = self.request.query_params.get('office', None)
        department = self.request.query_params.get('department', None)
        
        if office:
            queryset = queryset.filter(office_location=office)
        if department:
            queryset = queryset.filter(department=department)
            
        return queryset


class HealthCheckView(APIView):
    """
    API health check endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'service': 'Rejlers API System'
        })
