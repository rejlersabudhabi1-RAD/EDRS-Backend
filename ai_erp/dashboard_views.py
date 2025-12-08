"""
Role-based login redirection for AI ERP System
Routes users to appropriate dashboards based on their roles
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import logging

from ai_erp.models import UserERPProfile, AISystemLog
from ai_erp.rbac import RoleBasedAccessControl

logger = logging.getLogger(__name__)

@login_required
def dashboard_redirect(request):
    """
    Redirect users to appropriate dashboard based on their role
    This is the main entry point after login for the ERP system
    """
    
    try:
        # Get user's ERP profile
        try:
            erp_profile = request.user.erp_profile
            role = erp_profile.role
        except UserERPProfile.DoesNotExist:
            # User doesn't have ERP profile - redirect to profile setup
            messages.warning(request, 'Please complete your ERP profile setup to access the system.')
            return redirect('authentication:profile_setup')
        
        # Log the login
        AISystemLog.objects.create(
            user=request.user,
            log_type='user_login',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'role': role.code,
                'primary_domain': erp_profile.primary_domain,
                'login_time': request.session.get('login_time', None)
            },
            ip_address=get_client_ip(request),
            success=True
        )
        
        # Route based on role
        if role.code == 'SUPER_ADMIN':
            messages.success(request, f'Welcome to the Super Admin Dashboard, {request.user.get_full_name() or request.user.username}!')
            return redirect('ai_erp:admin_dashboard')
        
        elif role.code == 'PROJECT_MANAGER':
            messages.success(request, f'Welcome to the Project Manager Dashboard, {request.user.get_full_name() or request.user.username}!')
            return redirect('projects:project_list')  # Assuming this exists
        
        elif role.code in ['SENIOR_ENGINEER', 'ENGINEER']:
            messages.success(request, f'Welcome to the Engineering Dashboard, {request.user.get_full_name() or request.user.username}!')
            return redirect('simulation_management:dashboard')
        
        elif role.code == 'DRAWING_SPECIALIST':
            messages.success(request, f'Welcome to the Drawing Analysis Dashboard, {request.user.get_full_name() or request.user.username}!')
            return redirect('drawing_analysis:drawing_list')
        
        elif role.code == 'ANALYST':
            messages.success(request, f'Welcome to the Analysis Dashboard, {request.user.get_full_name() or request.user.username}!')
            return redirect('ai_erp:ai_monitoring')
        
        elif role.code == 'VIEWER':
            messages.success(request, f'Welcome, {request.user.get_full_name() or request.user.username}!')
            return redirect('projects:project_list')
        
        else:
            # Default fallback
            messages.info(request, f'Welcome, {request.user.get_full_name() or request.user.username}!')
            return redirect('projects:project_list')
    
    except Exception as e:
        logger.error(f"Dashboard redirect failed for user {request.user.username}: {str(e)}")
        messages.error(request, 'There was an issue accessing your dashboard. Please contact support if this continues.')
        
        # Log the error
        try:
            AISystemLog.objects.create(
                user=request.user,
                log_type='login_error',
                ai_model_used='system',
                processing_time=0,
                input_data={'error': str(e)},
                error_message=str(e),
                success=False
            )
        except:
            pass  # Don't let logging errors break the flow
        
        # Fallback to a safe page
        return redirect('api_root')

@login_required
def role_dashboard(request):
    """
    Main role-based dashboard view
    Shows different content based on user's role and permissions
    """
    
    try:
        erp_profile = request.user.erp_profile
        role = erp_profile.role
        
        # Get role-specific context
        context = get_role_dashboard_context(request.user, role)
        
        # Choose template based on role
        template_map = {
            'SUPER_ADMIN': 'dashboards/super_admin.html',
            'PROJECT_MANAGER': 'dashboards/project_manager.html',
            'SENIOR_ENGINEER': 'dashboards/senior_engineer.html',
            'ENGINEER': 'dashboards/engineer.html',
            'DRAWING_SPECIALIST': 'dashboards/drawing_specialist.html',
            'ANALYST': 'dashboards/analyst.html',
            'VIEWER': 'dashboards/viewer.html'
        }
        
        template = template_map.get(role.code, 'dashboards/default.html')
        
        return render(request, template, context)
    
    except UserERPProfile.DoesNotExist:
        return redirect('authentication:profile_setup')
    except Exception as e:
        logger.error(f"Role dashboard failed for user {request.user.username}: {str(e)}")
        messages.error(request, 'Dashboard unavailable. Please try again.')
        return redirect('api_root')

def get_role_dashboard_context(user, role):
    """Get context data for role-based dashboard"""
    
    context = {
        'user_profile': user.erp_profile,
        'role': role,
        'page_title': f'{role.name} Dashboard',
        'user_permissions': role.permissions,
    }
    
    # Add role-specific data
    if role.code == 'SUPER_ADMIN':
        from ai_erp.views import get_system_statistics, get_recent_activities, get_ai_usage_metrics
        context.update({
            'system_stats': get_system_statistics(),
            'recent_activities': get_recent_activities(limit=10),
            'ai_metrics': get_ai_usage_metrics(),
        })
    
    elif role.code == 'PROJECT_MANAGER':
        from projects.models import Project
        context.update({
            'managed_projects': Project.objects.filter(manager=user)[:10],
            'total_projects': Project.objects.filter(manager=user).count(),
        })
    
    elif role.code in ['SENIOR_ENGINEER', 'ENGINEER']:
        from simulation_management.models import SimulationProject
        context.update({
            'assigned_simulations': SimulationProject.objects.filter(assigned_engineer=user)[:10],
            'total_simulations': SimulationProject.objects.filter(assigned_engineer=user).count(),
        })
    
    elif role.code == 'DRAWING_SPECIALIST':
        from drawing_analysis.models import DrawingDocument
        context.update({
            'recent_drawings': DrawingDocument.objects.filter(uploaded_by=user)[:10],
            'total_drawings': DrawingDocument.objects.filter(uploaded_by=user).count(),
        })
    
    return context

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip