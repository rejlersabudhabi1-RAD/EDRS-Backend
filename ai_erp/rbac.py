"""
Role-Based Access Control (RBAC) System for Oil & Gas ERP
Handles user authentication, role management, and permission-based access control
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from functools import wraps
import json
import logging
from typing import List, Dict, Any, Optional
from authentication.models import RejlersUser
from ai_erp.models import ERPRole, UserERPProfile

logger = logging.getLogger(__name__)

class RoleBasedAccessControl:
    """Main RBAC handler for the ERP system"""
    
    @staticmethod
    def get_user_role(user: RejlersUser) -> Optional[ERPRole]:
        """Get user's ERP role"""
        try:
            profile = user.erp_profile
            return profile.role
        except UserERPProfile.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_permissions(user: RejlersUser) -> List[str]:
        """Get user's permissions list"""
        role = RoleBasedAccessControl.get_user_role(user)
        if role:
            return role.permissions
        return []
    
    @staticmethod
    def has_permission(user: RejlersUser, permission: str) -> bool:
        """Check if user has specific permission"""
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
            
        permissions = RoleBasedAccessControl.get_user_permissions(user)
        
        # Check for wildcard permission
        if '*' in permissions:
            return True
        
        # Check exact match
        if permission in permissions:
            return True
        
        # Check for wildcard patterns (e.g., 'drawing.*' matches 'drawing.read')
        for perm in permissions:
            if perm.endswith('*') and permission.startswith(perm[:-1]):
                return True
        
        return False
    
    @staticmethod
    def get_dashboard_url(user: RejlersUser) -> str:
        """Get appropriate dashboard URL based on user role"""
        role = RoleBasedAccessControl.get_user_role(user)
        
        if not role:
            return '/dashboard/'
        
        return role.redirect_url
    
    @staticmethod
    def can_access_domain(user: RejlersUser, domain: str) -> bool:
        """Check if user can access specific engineering domain"""
        try:
            profile = user.erp_profile
            return profile.can_access_domain(domain)
        except UserERPProfile.DoesNotExist:
            return False

def require_permission(permission: str):
    """Decorator to require specific permission for view access"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)
            
            if not RoleBasedAccessControl.has_permission(request.user, permission):
                return JsonResponse({
                    'error': 'Insufficient permissions',
                    'required_permission': permission
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(role_codes: List[str]):
    """Decorator to require specific roles for view access"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)
            
            user_role = RoleBasedAccessControl.get_user_role(request.user)
            if not user_role or user_role.code not in role_codes:
                return JsonResponse({
                    'error': 'Insufficient role privileges',
                    'required_roles': role_codes,
                    'user_role': user_role.code if user_role else None
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_permissions(permissions: List[str]):
    """Decorator to require specific permissions for view access"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)
            
            # Check if user has all required permissions
            for permission in permissions:
                if not RoleBasedAccessControl.has_permission(request.user, permission):
                    return JsonResponse({
                        'error': f'Missing required permission: {permission}',
                        'required_permissions': permissions,
                        'user_permissions': RoleBasedAccessControl.get_user_permissions(request.user)
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_domain_access(domain: str):
    """Decorator to require access to specific engineering domain"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)
            
            if not RoleBasedAccessControl.can_access_domain(request.user, domain):
                return JsonResponse({
                    'error': f'Access denied to {domain} domain',
                    'required_domain': domain
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

class SessionManager:
    """Manage user sessions and concurrent access"""
    
    @staticmethod
    def check_concurrent_sessions(user: RejlersUser) -> bool:
        """Check if user has exceeded concurrent session limit"""
        try:
            profile = user.erp_profile
            max_sessions = profile.max_concurrent_sessions
            
            # Get active sessions for user
            from django.contrib.sessions.models import Session
            from django.utils import timezone
            
            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            )
            
            user_sessions = 0
            for session in active_sessions:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(user.id):
                    user_sessions += 1
            
            return user_sessions < max_sessions
            
        except UserERPProfile.DoesNotExist:
            return True  # Allow if no profile exists
    
    @staticmethod
    def is_ip_allowed(user: RejlersUser, ip_address: str) -> bool:
        """Check if IP address is in user's whitelist"""
        try:
            profile = user.erp_profile
            
            # If no whitelist, allow all IPs
            if not profile.ip_whitelist:
                return True
            
            return ip_address in profile.ip_whitelist
            
        except UserERPProfile.DoesNotExist:
            return True
    
    @staticmethod
    def is_access_time_allowed(user: RejlersUser) -> bool:
        """Check if current time is within user's allowed access hours"""
        try:
            from datetime import datetime
            
            profile = user.erp_profile
            
            # If no access hours restriction, allow all times
            if not profile.access_hours:
                return True
            
            now = datetime.now()
            weekday = now.strftime('%A').lower()
            current_hour = now.hour
            
            if weekday in profile.access_hours:
                allowed_hours = profile.access_hours[weekday]
                start_hour = allowed_hours.get('start', 0)
                end_hour = allowed_hours.get('end', 23)
                
                return start_hour <= current_hour <= end_hour
            
            return False
            
        except UserERPProfile.DoesNotExist:
            return True

def enhanced_login_required(view_func):
    """Enhanced login decorator with RBAC checks"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        
        # Check concurrent sessions
        if not SessionManager.check_concurrent_sessions(request.user):
            return JsonResponse({
                'error': 'Maximum concurrent sessions exceeded',
                'action': 'logout_other_sessions'
            }, status=429)
        
        # Check IP whitelist
        client_ip = get_client_ip(request)
        if not SessionManager.is_ip_allowed(request.user, client_ip):
            return JsonResponse({
                'error': 'Access denied from this IP address',
                'ip': client_ip
            }, status=403)
        
        # Check access hours
        if not SessionManager.is_access_time_allowed(request.user):
            return JsonResponse({
                'error': 'Access denied outside allowed hours'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class PermissionMatrix:
    """Define permission matrix for different roles and actions"""
    
    PERMISSIONS = {
        # Drawing Analysis Permissions
        'drawing.upload': 'Upload technical drawings',
        'drawing.read': 'View drawings and analysis results',
        'drawing.analyze': 'Initiate AI drawing analysis',
        'drawing.comment': 'Add comments to drawings',
        'drawing.approve': 'Approve drawings and analyses',
        'drawing.delete': 'Delete drawings',
        'drawing.export': 'Export drawings and results',
        
        # Simulation Permissions
        'simulation.create': 'Create simulation projects',
        'simulation.read': 'View simulation results',
        'simulation.run': 'Execute simulations',
        'simulation.modify': 'Modify simulation parameters',
        'simulation.delete': 'Delete simulations',
        'simulation.ai_assist': 'Use AI simulation assistant',
        
        # Project Management Permissions
        'project.create': 'Create new projects',
        'project.read': 'View project information',
        'project.modify': 'Modify project details',
        'project.delete': 'Delete projects',
        'project.assign': 'Assign team members to projects',
        'project.financial': 'Access financial information',
        
        # AI Services Permissions
        'ai.query': 'Query AI assistant',
        'ai.advanced': 'Use advanced AI features',
        'ai.train': 'Train AI models',
        'ai.configure': 'Configure AI settings',
        
        # Administration Permissions
        'admin.users': 'Manage user accounts',
        'admin.roles': 'Manage roles and permissions',
        'admin.system': 'System administration',
        'admin.audit': 'View audit logs',
        'admin.reports': 'Generate system reports',
        
        # Domain-Specific Permissions
        'upstream.access': 'Access upstream domain',
        'midstream.access': 'Access midstream domain',
        'downstream.access': 'Access downstream domain',
        'offshore.access': 'Access offshore domain',
        'onshore.access': 'Access onshore domain',
        
        # Safety and Compliance
        'safety.analyze': 'Perform safety analysis',
        'compliance.check': 'Check regulatory compliance',
        'environmental.assess': 'Environmental impact assessment',
        
        # Data and Export
        'data.export': 'Export data and reports',
        'data.import': 'Import external data',
        'reports.generate': 'Generate reports',
        'reports.schedule': 'Schedule automated reports',
    }
    
    @classmethod
    def get_permission_description(cls, permission: str) -> str:
        """Get human-readable description of permission"""
        return cls.PERMISSIONS.get(permission, 'Unknown permission')
    
    @classmethod
    def get_all_permissions(cls) -> Dict[str, str]:
        """Get all available permissions with descriptions"""
        return cls.PERMISSIONS.copy()

def create_default_roles():
    """Create default ERP roles with appropriate permissions"""
    
    roles_config = [
        {
            'name': 'Super Administrator',
            'code': 'SUPER_ADMIN',
            'description': 'Full system access and control',
            'permissions': ['*'],
            'redirect_url': '/ai-erp/admin-dashboard/'
        },
        {
            'name': 'Project Manager',
            'code': 'PROJECT_MANAGER',
            'description': 'Project management and oversight',
            'permissions': [
                'project.*', 'drawing.read', 'drawing.comment', 'drawing.approve',
                'simulation.read', 'team.read', 'reports.generate', 'ai.query'
            ],
            'redirect_url': '/pm/dashboard/'
        },
        {
            'name': 'Senior Engineer',
            'code': 'SENIOR_ENGINEER',
            'description': 'Full engineering capabilities',
            'permissions': [
                'drawing.*', 'simulation.*', 'ai.query', 'ai.advanced',
                'project.read', 'project.modify', 'safety.analyze',
                'compliance.check', 'reports.generate'
            ],
            'redirect_url': '/engineer/dashboard/'
        },
        {
            'name': 'Engineer',
            'code': 'ENGINEER',
            'description': 'Standard engineering access',
            'permissions': [
                'drawing.read', 'drawing.upload', 'drawing.analyze', 'drawing.comment',
                'simulation.create', 'simulation.read', 'simulation.run',
                'ai.query', 'project.read', 'reports.generate'
            ],
            'redirect_url': '/engineer/workspace/'
        },
        {
            'name': 'Analyst',
            'code': 'ANALYST',
            'description': 'Analysis and reporting access',
            'permissions': [
                'drawing.read', 'simulation.read', 'ai.query',
                'reports.generate', 'data.export', 'project.read'
            ],
            'redirect_url': '/analyst/dashboard/'
        },
        {
            'name': 'Viewer',
            'code': 'VIEWER',
            'description': 'Read-only access to approved content',
            'permissions': [
                'drawing.read', 'simulation.read', 'project.read', 'reports.generate'
            ],
            'redirect_url': '/viewer/dashboard/'
        }
    ]
    
    created_roles = []
    for role_config in roles_config:
        role, created = ERPRole.objects.get_or_create(
            code=role_config['code'],
            defaults={
                'name': role_config['name'],
                'description': role_config['description'],
                'permissions': role_config['permissions'],
                'redirect_url': role_config['redirect_url']
            }
        )
        if created:
            created_roles.append(role)
            logger.info(f"Created role: {role.name}")
    
    return created_roles

# Middleware for RBAC
class RBACMiddleware:
    """Middleware to enforce RBAC across all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        if request.user.is_authenticated:
            # Log user activity
            self._log_user_activity(request)
            
            # Update last login IP
            self._update_last_login_ip(request)
        
        response = self.get_response(request)
        return response
    
    def _log_user_activity(self, request):
        """Log user activity for audit trail"""
        try:
            from ai_erp.models import AISystemLog
            
            # Only log significant actions, not every page view
            significant_paths = ['/api/', '/upload/', '/analyze/', '/simulate/']
            
            if any(path in request.path for path in significant_paths):
                AISystemLog.objects.create(
                    user=request.user,
                    log_type='user_activity',
                    ai_model_used='system',
                    processing_time=0,
                    input_data={
                        'path': request.path,
                        'method': request.method,
                        'timestamp': str(timezone.now())
                    },
                    ip_address=get_client_ip(request)
                )
        except Exception as e:
            logger.warning(f"Failed to log user activity: {str(e)}")
    
    def _update_last_login_ip(self, request):
        """Update user's last login IP"""
        try:
            profile = request.user.erp_profile
            current_ip = get_client_ip(request)
            
            if profile.last_login_ip != current_ip:
                profile.last_login_ip = current_ip
                profile.save(update_fields=['last_login_ip'])
        except Exception:
            pass  # Silently fail if profile doesn't exist