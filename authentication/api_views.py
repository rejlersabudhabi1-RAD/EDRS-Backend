"""
Authentication API Views for Rejlers AI-Powered ERP System
Comprehensive login, registration, and user management endpoints
"""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

from authentication.models import RejlersUser
from ai_erp.models import ERPRole, UserERPProfile
from ai_erp.rbac import RoleBasedAccessControl

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token login with role-based redirection"""
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if not user:
            logger.warning(f"Failed login attempt for: {email}")
            return Response({
                'error': 'Invalid credentials',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Account is deactivated',
                'success': False
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Get user profile and role information
        try:
            erp_profile = UserERPProfile.objects.select_related('role').get(user=user)
            role_data = {
                'name': erp_profile.role.name,
                'code': erp_profile.role.code,
                'redirect_url': erp_profile.role.redirect_url,
                'permissions': erp_profile.role.permissions
            }
            profile_data = {
                'experience_level': erp_profile.experience_level,
                'primary_domain': erp_profile.primary_domain,
                'ai_assistant_enabled': erp_profile.ai_assistant_enabled
            }
        except UserERPProfile.DoesNotExist:
            role_data = {
                'name': 'USER',
                'code': 'U',
                'redirect_url': '/dashboard/',
                'permissions': ['basic.read']
            }
            profile_data = {}
        
        # Update login tracking
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Log successful login
        logger.info(f"Successful login: {user.email} ({role_data['name']})")
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            },
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            },
            'role': role_data,
            'profile': profile_data,
            'redirect_url': role_data['redirect_url']
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """User registration endpoint"""
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return Response({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Check if user already exists
        if RejlersUser.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        if len(password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = RejlersUser.objects.create(
            email=email,
            username=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=make_password(password),
            department=data.get('department', ''),
            position=data.get('position', ''),
            phone=data.get('phone', ''),
            is_active=True
        )
        
        # Assign default role (Engineer)
        try:
            default_role = ERPRole.objects.get(name='ENGINEER')
        except ERPRole.DoesNotExist:
            # Create default engineer role if it doesn't exist
            default_role = ERPRole.objects.create(
                name='ENGINEER',
                code='ENG',
                description='Standard engineering access',
                permissions=['drawing.read', 'drawing.analyze', 'simulation.read'],
                redirect_url='/engineer/workspace/',
                is_active=True
            )
        
        # Create user profile
        UserERPProfile.objects.create(
            user=user,
            role=default_role,
            experience_level=data.get('experience_level', 'junior'),
            primary_domain=data.get('primary_domain', 'process'),
            ai_assistant_enabled=True,
            preferred_ai_model='gpt-4o-mini',
            ai_analysis_level='basic'
        )
        
        logger.info(f"New user registered: {email}")
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({
            'error': 'Registration failed. Please try again.',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        })
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'error': 'Logout failed',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile information"""
    try:
        user = request.user
        
        try:
            erp_profile = UserERPProfile.objects.select_related('role').get(user=user)
            role_data = {
                'name': erp_profile.role.name,
                'code': erp_profile.role.code,
                'description': erp_profile.role.description,
                'permissions': erp_profile.role.permissions,
                'redirect_url': erp_profile.role.redirect_url
            }
            profile_data = {
                'experience_level': erp_profile.experience_level,
                'primary_domain': erp_profile.primary_domain,
                'secondary_domains': erp_profile.secondary_domains,
                'certifications': erp_profile.certifications,
                'specializations': erp_profile.specializations,
                'ai_assistant_enabled': erp_profile.ai_assistant_enabled,
                'preferred_ai_model': erp_profile.preferred_ai_model,
                'ai_analysis_level': erp_profile.ai_analysis_level,
                'total_drawings_analyzed': erp_profile.total_drawings_analyzed,
                'total_simulations_run': erp_profile.total_simulations_run,
                'ai_queries_count': erp_profile.ai_queries_count
            }
        except UserERPProfile.DoesNotExist:
            role_data = {'name': 'USER', 'permissions': []}
            profile_data = {}
        
        return Response({
            'success': True,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'department': user.department,
                'position': user.position,
                'phone': user.phone,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat()
            },
            'role': role_data,
            'profile': profile_data
        })
        
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response({
            'error': 'Failed to fetch profile',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_roles(request):
    """Get available roles for registration"""
    try:
        roles = ERPRole.objects.filter(is_active=True).values('name', 'code', 'description')
        return Response({
            'success': True,
            'roles': list(roles)
        })
    except Exception as e:
        return Response({
            'error': 'Failed to fetch roles',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add timezone import
from django.utils import timezone