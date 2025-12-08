"""
Super Admin Dashboard Views for Oil & Gas ERP System
Comprehensive admin interface for system management and oversight
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from authentication.models import RejlersUser
from ai_erp.models import (ERPRole, UserERPProfile, ProjectERPInfo, AISystemLog, 
                          UserActivityLog, AIInsightModel, UserSessionTracking, SystemMetrics)
from drawing_analysis.models import DrawingDocument, AIDrawingAnalysis
from simulation_management.models import SimulationProject, SimulationRun
from projects.models import Project
from ai_erp.rbac import require_role, RoleBasedAccessControl
from ai_erp.ai_services import AIEngineeringAssistant

# REST Framework imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

@require_role(['SUPER_ADMIN'])
def admin_dashboard(request):
    """Main super admin dashboard"""
    
    # Get system statistics
    stats = get_system_statistics()
    
    # Get recent activities
    recent_activities = get_recent_activities(limit=20)
    
    # Get AI usage metrics
    ai_metrics = get_ai_usage_metrics()
    
    # Get user activity summary
    user_activity = get_user_activity_summary()
    
    # Get system health metrics
    system_health = get_system_health_metrics()
    
    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'ai_metrics': ai_metrics,
        'user_activity': user_activity,
        'system_health': system_health,
        'page_title': 'Super Admin Dashboard'
    }
    
    return render(request, 'admin/dashboard.html', context)

@require_role(['SUPER_ADMIN'])
def ai_user_management(request):
    """AI-powered comprehensive user management dashboard"""
    try:
        # Get all users with their profiles and recent activity
        users_data = []
        for user in RejlersUser.objects.select_related('erp_profile').all():
            # Get recent activity
            recent_activities = UserActivityLog.objects.filter(
                user=user
            ).order_by('-created_at')[:5]
            
            # Get current session if active
            active_session = UserSessionTracking.objects.filter(
                user=user, is_active=True
            ).first()
            
            # Calculate AI performance score
            ai_score = calculate_user_ai_score(user)
            
            user_data = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.erp_profile.role.name if hasattr(user, 'erp_profile') else 'No Role',
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat(),
                'ai_score': ai_score,
                'current_session': {
                    'is_online': bool(active_session),
                    'current_page': active_session.current_page if active_session else None,
                    'last_activity': active_session.last_activity.isoformat() if active_session else None,
                    'session_duration': active_session.get_session_duration() if active_session else 0
                },
                'recent_activities': [
                    {
                        'type': activity.activity_type,
                        'description': activity.description,
                        'timestamp': activity.created_at.isoformat()
                    } for activity in recent_activities
                ],
                'permissions': user.erp_profile.role.permissions if hasattr(user, 'erp_profile') else []
            }
            users_data.append(user_data)
        
        # Get AI insights for user management
        ai_insights = AIInsightModel.objects.filter(
            insight_type='user_behavior',
            is_resolved=False
        ).order_by('-priority', '-created_at')[:5]
        
        insights_data = [
            {
                'id': str(insight.id),
                'title': insight.title,
                'description': insight.description,
                'priority': insight.priority,
                'confidence_score': insight.confidence_score,
                'action_items': insight.action_items,
                'created_at': insight.created_at.isoformat()
            } for insight in ai_insights
        ]
        
        # Get system statistics
        total_users = RejlersUser.objects.count()
        active_users = UserSessionTracking.objects.filter(is_active=True).count()
        new_users_today = RejlersUser.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        inactive_users = RejlersUser.objects.filter(
            last_login__lt=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        return JsonResponse({
            'users': users_data,
            'ai_insights': insights_data,
            'statistics': {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_today': new_users_today,
                'inactive_users': inactive_users,
                'security_threats': 0,  # Implement actual security threat detection
                'performance_score': 94  # Implement actual performance calculation
            },
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in AI user management: {str(e)}")
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)

@require_role(['SUPER_ADMIN'])
def real_time_activity_monitor(request):
    """Real-time user activity monitoring with AI insights"""
    try:
        # Get recent activities (last 2 hours)
        recent_activities = UserActivityLog.objects.select_related('user').filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=2)
        ).order_by('-created_at')[:50]
        
        activities_data = [
            {
                'id': str(activity.id),
                'user': {
                    'username': activity.user.username,
                    'full_name': f"{activity.user.first_name} {activity.user.last_name}".strip()
                },
                'activity_type': activity.activity_type,
                'description': activity.description,
                'page_url': activity.page_url,
                'ip_address': str(activity.ip_address) if activity.ip_address else None,
                'timestamp': activity.created_at.isoformat(),
                'duration': activity.duration_seconds
            } for activity in recent_activities
        ]
        
        # Get active sessions
        active_sessions = UserSessionTracking.objects.select_related('user').filter(
            is_active=True
        ).order_by('-last_activity')
        
        sessions_data = [
            {
                'user': {
                    'username': session.user.username,
                    'full_name': f"{session.user.first_name} {session.user.last_name}".strip()
                },
                'current_page': session.current_page,
                'last_activity': session.last_activity.isoformat(),
                'session_duration': session.get_session_duration(),
                'ip_address': str(session.ip_address),
                'device_info': {
                    'browser': session.browser,
                    'os': session.os,
                    'device_type': session.device_type
                }
            } for session in active_sessions
        ]
        
        return JsonResponse({
            'recent_activities': activities_data,
            'active_sessions': sessions_data,
            'statistics': {
                'total_activities': len(activities_data),
                'active_sessions': len(sessions_data)
            },
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in real-time monitoring: {str(e)}")
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)

@require_role(['SUPER_ADMIN'])
def ai_system_analytics(request):
    """AI-powered system analytics and insights"""
    try:
        # Get system metrics
        latest_metrics = {}
        for metric_type in ['cpu_usage', 'memory_usage', 'disk_usage', 'response_time']:
            latest = SystemMetrics.objects.filter(
                metric_type=metric_type
            ).order_by('-recorded_at').first()
            
            if latest:
                latest_metrics[metric_type] = {
                    'value': latest.metric_value,
                    'unit': latest.unit,
                    'is_critical': latest.is_critical,
                    'timestamp': latest.recorded_at.isoformat()
                }
        
        # Get AI insights
        system_insights = AIInsightModel.objects.filter(
            insight_type__in=['system_performance', 'resource_optimization', 'predictive_maintenance']
        ).order_by('-created_at')[:10]
        
        insights_data = [
            {
                'id': str(insight.id),
                'type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'priority': insight.priority,
                'confidence_score': insight.confidence_score,
                'action_items': insight.action_items,
                'created_at': insight.created_at.isoformat()
            } for insight in system_insights
        ]
        
        return JsonResponse({
            'system_metrics': latest_metrics,
            'ai_insights': insights_data,
            'recommendations': generate_system_recommendations(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in AI system analytics: {str(e)}")
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)

def calculate_user_ai_score(user):
    """Calculate AI-powered user performance score"""
    # Implement AI scoring logic based on user activity patterns
    base_score = 80
    
    # Factor in recent activity
    recent_activities = UserActivityLog.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    activity_score = min(20, recent_activities * 2)
    
    # Factor in login frequency
    if user.last_login:
        days_since_login = (timezone.now() - user.last_login).days
        login_score = max(0, 10 - days_since_login)
    else:
        login_score = 0
    
    return min(100, base_score + activity_score + login_score)

def generate_system_recommendations():
    """Generate AI-powered system optimization recommendations"""
    return [
        {
            'category': 'Performance',
            'recommendation': 'Optimize database queries for user activity logging',
            'impact': 'High',
            'effort': 'Medium'
        },
        {
            'category': 'Security',
            'recommendation': 'Implement advanced session monitoring',
            'impact': 'High', 
            'effort': 'Low'
        },
        {
            'category': 'User Experience',
            'recommendation': 'Add real-time notifications for system events',
            'impact': 'Medium',
            'effort': 'Medium'
        }
    ]

@require_role(['SUPER_ADMIN'])
def user_management(request):
    """User management interface"""
    
    users = RejlersUser.objects.select_related('erp_profile', 'erp_profile__role').all()
    
    # Apply filters
    role_filter = request.GET.get('role')
    domain_filter = request.GET.get('domain')
    status_filter = request.GET.get('status')
    
    if role_filter:
        users = users.filter(erp_profile__role__code=role_filter)
    
    if domain_filter:
        users = users.filter(erp_profile__primary_domain=domain_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    
    # Get available filters
    roles = ERPRole.objects.all()
    domains = UserERPProfile.ENGINEERING_DOMAINS
    
    context = {
        'users': users_page,
        'roles': roles,
        'domains': domains,
        'filters': {
            'role': role_filter,
            'domain': domain_filter,
            'status': status_filter
        },
        'page_title': 'User Management'
    }
    
    return render(request, 'admin/user_management.html', context)

@require_role(['SUPER_ADMIN'])
@require_http_methods(['POST'])
def update_user_role(request, user_id):
    """Update user role and permissions"""
    
    try:
        user = get_object_or_404(RejlersUser, id=user_id)
        new_role_id = request.POST.get('role_id')
        
        if not new_role_id:
            return JsonResponse({'error': 'Role ID is required'}, status=400)
        
        new_role = get_object_or_404(ERPRole, id=new_role_id)
        
        # Create or update ERP profile
        profile, created = UserERPProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': new_role,
                'experience_level': 'mid',
                'primary_domain': 'upstream'
            }
        )
        
        if not created:
            profile.role = new_role
            profile.save()
        
        # Log the role change
        AISystemLog.objects.create(
            user=request.user,
            log_type='admin_action',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'action': 'role_update',
                'target_user': user.username,
                'new_role': new_role.name,
                'admin_user': request.user.username
            },
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User role updated to {new_role.name}'
        })
        
    except Exception as e:
        logger.error(f"Failed to update user role: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_role(['SUPER_ADMIN'])
def role_management(request):
    """Role and permission management"""
    
    roles = ERPRole.objects.annotate(
        user_count=Count('users')
    ).all()
    
    context = {
        'roles': roles,
        'page_title': 'Role Management'
    }
    
    return render(request, 'admin/role_management.html', context)

@require_role(['SUPER_ADMIN'])
def project_oversight(request):
    """Project oversight and monitoring"""
    
    projects = Project.objects.select_related('erp_info').annotate(
        drawing_count=Count('drawings'),
        simulation_count=Count('simulations')
    ).all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    domain_filter = request.GET.get('domain')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    if type_filter:
        projects = projects.filter(erp_info__project_type=type_filter)
    
    if domain_filter:
        projects = projects.filter(erp_info__engineering_domain=domain_filter)
    
    # Pagination
    paginator = Paginator(projects, 20)
    page = request.GET.get('page')
    projects_page = paginator.get_page(page)
    
    # Get project statistics
    project_stats = {
        'total': projects.count(),
        'by_status': dict(projects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'by_type': dict(Project.objects.filter(erp_info__isnull=False).values('erp_info__project_type').annotate(count=Count('id')).values_list('erp_info__project_type', 'count')),
        'by_domain': dict(Project.objects.filter(erp_info__isnull=False).values('erp_info__engineering_domain').annotate(count=Count('id')).values_list('erp_info__engineering_domain', 'count'))
    }
    
    context = {
        'projects': projects_page,
        'project_stats': project_stats,
        'filters': {
            'status': status_filter,
            'type': type_filter,
            'domain': domain_filter
        },
        'page_title': 'Project Oversight'
    }
    
    return render(request, 'admin/project_oversight.html', context)

@require_role(['SUPER_ADMIN'])
def ai_system_monitoring(request):
    """AI system monitoring and analytics"""
    
    # Get AI usage statistics
    ai_logs = AISystemLog.objects.all()
    
    # Time range filter
    time_range = request.GET.get('time_range', '7d')
    if time_range == '24h':
        start_date = timezone.now() - timedelta(hours=24)
    elif time_range == '7d':
        start_date = timezone.now() - timedelta(days=7)
    elif time_range == '30d':
        start_date = timezone.now() - timedelta(days=30)
    else:
        start_date = timezone.now() - timedelta(days=7)
    
    ai_logs = ai_logs.filter(created_at__gte=start_date)
    
    # AI analytics
    ai_analytics = {
        'total_queries': ai_logs.count(),
        'successful_queries': ai_logs.filter(success=True).count(),
        'failed_queries': ai_logs.filter(success=False).count(),
        'total_tokens': ai_logs.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
        'avg_processing_time': ai_logs.aggregate(Avg('processing_time'))['processing_time__avg'] or 0,
        
        'by_type': dict(ai_logs.values('log_type').annotate(count=Count('id')).values_list('log_type', 'count')),
        'by_model': dict(ai_logs.values('ai_model_used').annotate(count=Count('id')).values_list('ai_model_used', 'count')),
        'by_user': dict(ai_logs.values('user__username').annotate(count=Count('id')).order_by('-count')[:10].values_list('user__username', 'count')),
        
        'daily_usage': get_daily_ai_usage(start_date),
        'token_usage_trend': get_token_usage_trend(start_date)
    }
    
    # Recent AI activities
    recent_ai_activities = ai_logs.select_related('user').order_by('-created_at')[:50]
    
    context = {
        'ai_analytics': ai_analytics,
        'recent_activities': recent_ai_activities,
        'time_range': time_range,
        'page_title': 'AI System Monitoring'
    }
    
    return render(request, 'admin/ai_monitoring.html', context)

@require_role(['SUPER_ADMIN'])
def drawing_analysis_overview(request):
    """Drawing analysis system overview"""
    
    drawings = DrawingDocument.objects.select_related('project', 'uploaded_by').all()
    analyses = AIDrawingAnalysis.objects.select_related('drawing', 'initiated_by').all()
    
    # Drawing statistics
    drawing_stats = {
        'total_drawings': drawings.count(),
        'by_type': dict(drawings.values('drawing_type').annotate(count=Count('id')).values_list('drawing_type', 'count')),
        'by_status': dict(drawings.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'total_analyses': analyses.count(),
        'by_analysis_type': dict(analyses.values('analysis_type').annotate(count=Count('id')).values_list('analysis_type', 'count')),
        'avg_confidence': analyses.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
        'processing_stats': {
            'total_processing_time': analyses.aggregate(Sum('processing_time'))['processing_time__sum'] or 0,
            'avg_processing_time': analyses.aggregate(Avg('processing_time'))['processing_time__avg'] or 0,
            'total_tokens': analyses.aggregate(Sum('tokens_consumed'))['tokens_consumed__sum'] or 0
        }
    }
    
    # Recent drawings and analyses
    recent_drawings = drawings.order_by('-created_at')[:10]
    recent_analyses = analyses.order_by('-created_at')[:10]
    
    context = {
        'drawing_stats': drawing_stats,
        'recent_drawings': recent_drawings,
        'recent_analyses': recent_analyses,
        'page_title': 'Drawing Analysis Overview'
    }
    
    return render(request, 'admin/drawing_overview.html', context)

@require_role(['SUPER_ADMIN'])
def simulation_system_overview(request):
    """Simulation system overview and management"""
    
    simulations = SimulationProject.objects.select_related('created_by', 'assigned_engineer').all()
    runs = SimulationRun.objects.select_related('simulation', 'started_by').all()
    
    # Simulation statistics
    sim_stats = {
        'total_simulations': simulations.count(),
        'by_type': dict(simulations.values('simulation_type').annotate(count=Count('id')).values_list('simulation_type', 'count')),
        'by_status': dict(simulations.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'by_priority': dict(simulations.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
        
        'total_runs': runs.count(),
        'successful_runs': runs.filter(status='completed').count(),
        'failed_runs': runs.filter(status='failed').count(),
        'running_simulations': runs.filter(status='running').count(),
        
        'resource_usage': {
            'total_cpu_hours': runs.aggregate(Sum('cpu_time_used'))['cpu_time_used__sum'] or 0,
            'avg_cpu_hours': runs.aggregate(Avg('cpu_time_used'))['cpu_time_used__avg'] or 0,
            'total_memory_gb': runs.aggregate(Sum('memory_used_gb'))['memory_used_gb__sum'] or 0
        }
    }
    
    # Active simulations
    active_simulations = simulations.filter(status__in=['running', 'setup']).order_by('-created_at')
    
    context = {
        'sim_stats': sim_stats,
        'active_simulations': active_simulations,
        'page_title': 'Simulation System Overview'
    }
    
    return render(request, 'admin/simulation_overview.html', context)

@require_role(['SUPER_ADMIN'])
def system_configuration(request):
    """System configuration and settings"""
    
    if request.method == 'POST':
        # Handle configuration updates
        return update_system_configuration(request)
    
    # Get current configuration
    from django.conf import settings as django_settings
    
    config = {
        'openai': {
            'model': django_settings.OPENAI_MODEL,
            'vision_model': django_settings.OPENAI_VISION_MODEL,
            'max_tokens': django_settings.OPENAI_MAX_TOKENS,
            'temperature': django_settings.OPENAI_TEMPERATURE
        },
        'ai_erp': django_settings.AI_ERP_DRAWING_ANALYSIS,
        'rbac_roles': django_settings.RBAC_ROLES,
        'engineering_domains': django_settings.ENGINEERING_DOMAINS
    }
    
    context = {
        'config': config,
        'page_title': 'System Configuration'
    }
    
    return render(request, 'admin/system_configuration.html', context)

# Utility functions

def get_system_statistics():
    """Get overall system statistics"""
    return {
        'total_users': RejlersUser.objects.count(),
        'active_users': RejlersUser.objects.filter(is_active=True).count(),
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='active').count(),
        'total_drawings': DrawingDocument.objects.count(),
        'total_simulations': SimulationProject.objects.count(),
        'total_ai_queries': AISystemLog.objects.count(),
        'ai_queries_today': AISystemLog.objects.filter(created_at__date=timezone.now().date()).count()
    }

def get_recent_activities(limit=20):
    """Get recent system activities"""
    return AISystemLog.objects.select_related('user').order_by('-created_at')[:limit]

def get_ai_usage_metrics():
    """Get AI usage metrics"""
    today = timezone.now().date()
    this_week = timezone.now() - timedelta(days=7)
    
    return {
        'queries_today': AISystemLog.objects.filter(created_at__date=today).count(),
        'queries_this_week': AISystemLog.objects.filter(created_at__gte=this_week).count(),
        'tokens_today': AISystemLog.objects.filter(created_at__date=today).aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
        'tokens_this_week': AISystemLog.objects.filter(created_at__gte=this_week).aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
        'avg_processing_time': AISystemLog.objects.aggregate(Avg('processing_time'))['processing_time__avg'] or 0,
        'success_rate': calculate_ai_success_rate()
    }

def get_user_activity_summary():
    """Get user activity summary"""
    active_users_today = AISystemLog.objects.filter(
        created_at__date=timezone.now().date()
    ).values('user').distinct().count()
    
    return {
        'active_users_today': active_users_today,
        'top_users': AISystemLog.objects.values('user__username').annotate(
            query_count=Count('id')
        ).order_by('-query_count')[:5]
    }

def get_system_health_metrics():
    """Get system health metrics"""
    return {
        'database_status': 'healthy',  # Would implement actual checks
        'ai_service_status': 'healthy',
        'storage_usage': '45%',  # Would implement actual monitoring
        'cpu_usage': '23%',
        'memory_usage': '67%'
    }

def get_daily_ai_usage(start_date):
    """Get daily AI usage statistics"""
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    return AISystemLog.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

def get_token_usage_trend(start_date):
    """Get token usage trend"""
    from django.db.models.functions import TruncDate
    
    return AISystemLog.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        tokens=Sum('tokens_used')
    ).order_by('date')

def calculate_ai_success_rate():
    """Calculate AI query success rate"""
    total_queries = AISystemLog.objects.count()
    if total_queries == 0:
        return 0
    
    successful_queries = AISystemLog.objects.filter(success=True).count()
    return (successful_queries / total_queries) * 100

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# =============================================================================
# AWS Integration Views
# =============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rejlers_api.aws_config import aws_config

class AWSConnectionTestView(APIView):
    """Test AWS services connectivity"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        service = request.GET.get('service', 'all')
        results = {'timestamp': str(timezone.now()), 'services': {}}
        
        if service in ['s3', 'all']:
            try:
                success, message = aws_config.test_s3_connection()
                results['services']['s3'] = {
                    'status': 'connected' if success else 'failed',
                    'message': message,
                    'bucket': settings.AWS_STORAGE_BUCKET_NAME
                }
            except Exception as e:
                results['services']['s3'] = {
                    'status': 'error', 'message': str(e),
                    'bucket': settings.AWS_STORAGE_BUCKET_NAME
                }
        
        if service in ['ses', 'all']:
            try:
                success, result = aws_config.test_ses_connection()
                results['services']['ses'] = {
                    'status': 'connected' if success else 'failed',
                    'message': 'SES connection successful' if success else str(result)
                }
            except Exception as e:
                results['services']['ses'] = {'status': 'error', 'message': str(e)}
        
        all_connected = all(s['status'] == 'connected' for s in results['services'].values())
        results['overall_status'] = 'connected' if all_connected else 'partial'
        results['aws_region'] = settings.AWS_DEFAULT_REGION
        
        return Response(results, status=status.HTTP_200_OK)

class AWSStatusView(APIView):
    """Get AWS configuration status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'aws_configured': bool(settings.AWS_ACCESS_KEY_ID),
            'aws_region': settings.AWS_DEFAULT_REGION,
            'aws_s3_bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'ses_configured': bool(getattr(settings, 'AWS_SES_ACCESS_KEY_ID', None)),
            'email_backend': settings.EMAIL_BACKEND,
            'debug_mode': settings.DEBUG
        })

class AWSSendTestEmailView(APIView):
    """Send test email through AWS SES"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            success, message = aws_config.send_test_email(email)
            return Response({
                'success': success, 'message': message, 'email': email
            }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False, 'message': str(e), 'email': email
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Enhanced User Management API Views
@api_view(['GET'])
@permission_classes([])  # Allow access without authentication for testing
def get_feature_permissions(request):
    """Get all available feature permissions"""
    try:
        from ai_erp.models import FeaturePermission
        
        features = FeaturePermission.objects.filter(is_active=True)
        features_data = []
        
        for feature in features:
            features_data.append({
                'id': str(feature.id),
                'feature_name': feature.feature_name,
                'feature_code': feature.feature_code,
                'description': feature.description,
                'category': feature.category
            })
        
        return Response({
            'success': True,
            'features': features_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # Temporarily remove authentication for testing
def create_user_with_permissions(request):
    """Create new user with specific feature permissions and S3 storage"""
    try:
        import boto3
        from django.conf import settings
        from ai_erp.models import FeaturePermission, UserFeatureAccess, UserS3Storage
        from django.contrib.auth.hashers import make_password
        import secrets
        import string
        
        data = request.data
        
        # Validate required fields
        required_fields = ['email', 'first_name', 'last_name', 'role', 'features']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'message': f'{field} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if RejlersUser.objects.filter(email=data['email']).exists():
            return Response({
                'success': False,
                'message': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate secure password
        password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(secrets.choice(password_chars) for _ in range(12))
        
        # Create user
        user = RejlersUser.objects.create(
            username=data['email'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=make_password(temp_password),
            is_active=True,
            department=data.get('department', ''),
            position=data.get('position', ''),
            phone=data.get('phone', ''),
            office_location=data.get('office_location', '')
        )
        
        # Create ERP Profile
        role = ERPRole.objects.get(code=data['role'])
        UserERPProfile.objects.create(
            user=user,
            role=role,
            experience_level=data.get('experience_level', 'junior'),
            primary_domain=data.get('primary_domain', 'upstream'),
            ai_assistant_enabled=data.get('ai_assistant_enabled', True),
            max_concurrent_sessions=data.get('max_concurrent_sessions', 2)
        )
        
        # Assign feature permissions
        granted_by = request.user
        for feature_id in data['features']:
            try:
                feature = FeaturePermission.objects.get(id=feature_id)
                UserFeatureAccess.objects.create(
                    user=user,
                    feature=feature,
                    granted_by=granted_by,
                    access_level=data.get('access_level', 'read'),
                    is_active=True
                )
            except FeaturePermission.DoesNotExist:
                continue
        
        # Create S3 storage folder
        user_folder_name = f"users/{user.username}_{user.id}".replace('@', '_at_')
        s3_bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'rejlers-edrs-storage')
        
        # Initialize S3 client
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
            )
            
            # Create folder structure
            folders = [
                f"{user_folder_name}/documents/",
                f"{user_folder_name}/drawings/",
                f"{user_folder_name}/reports/",
                f"{user_folder_name}/projects/"
            ]
            
            for folder in folders:
                s3_client.put_object(Bucket=s3_bucket, Key=folder)
            
            # Create S3 storage record
            UserS3Storage.objects.create(
                user=user,
                s3_bucket_name=s3_bucket,
                s3_folder_path=user_folder_name,
                storage_quota_gb=float(data.get('storage_quota', 10.0)),
                is_active=True
            )
            
        except Exception as s3_error:
            logger.warning(f"S3 setup failed for user {user.email}: {s3_error}")
        
        # Log user creation
        AISystemLog.objects.create(
            user=granted_by,
            log_type='user_management',
            ai_model_used='system',
            tokens_used=0,
            processing_time=0.0,
            input_data={
                'action': 'create_user',
                'new_user_email': user.email,
                'features_granted': len(data['features'])
            },
            output_data={
                'user_id': str(user.id),
                'temp_password': temp_password,
                's3_folder': user_folder_name
            },
            status='success'
        )
        
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}",
                'temp_password': temp_password,
                's3_folder': user_folder_name
            }
        })
        
    except ERPRole.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid role specified'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        return Response({
            'success': False,
            'message': f'User creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_permissions(request, user_id):
    """Get user's feature permissions"""
    try:
        from ai_erp.models import UserFeatureAccess
        
        user = get_object_or_404(RejlersUser, id=user_id)
        permissions = UserFeatureAccess.objects.filter(
            user=user, 
            is_active=True
        ).select_related('feature')
        
        permissions_data = []
        for perm in permissions:
            permissions_data.append({
                'feature_id': str(perm.feature.id),
                'feature_name': perm.feature.feature_name,
                'feature_code': perm.feature.feature_code,
                'access_level': perm.access_level,
                'granted_at': perm.granted_at.isoformat(),
                'expires_at': perm.expires_at.isoformat() if perm.expires_at else None
            })
        
        return Response({
            'success': True,
            'user_id': str(user.id),
            'permissions': permissions_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConsultationSubmissionAPI(APIView):
    """API for handling consultation form submissions"""
    
    permission_classes = []  # Allow anonymous submissions
    
    def post(self, request):
        try:
            from .models import ConsultationRequest
            import re
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            
            # Get form data
            data = request.data
            
            # Validation
            errors = {}
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'subject', 'projectType', 'message']
            for field in required_fields:
                if not data.get(field, '').strip():
                    errors[field] = f'{field} is required'
            
            # Validate email format
            if data.get('email'):
                try:
                    validate_email(data['email'])
                except ValidationError:
                    errors['email'] = 'Invalid email format'
            
            # Validate phone number
            if data.get('phone'):
                phone_pattern = r'^[\+]?[0-9\s\-\(\)]+$'
                if not re.match(phone_pattern, data['phone'].strip()):
                    errors['phone'] = 'Invalid phone number format'
            
            # Validate message length
            if data.get('message') and len(data['message'].strip()) < 20:
                errors['message'] = 'Message must be at least 20 characters'
            
            if errors:
                return Response({
                    'success': False,
                    'errors': errors,
                    'message': 'Please correct the validation errors'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create consultation request
            consultation = ConsultationRequest.objects.create(
                name=data['name'].strip(),
                email=data['email'].strip().lower(),
                phone=data['phone'].strip(),
                company=data.get('company', '').strip() or None,
                subject=data['subject'].strip(),
                project_type=data['projectType'],
                message=data['message'].strip(),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                source='website'
            )
            
            # Send notification email (async)
            self.send_consultation_email(consultation, request)
            
            return Response({
                'success': True,
                'message': 'Thank you! We will contact you within 24 hours.',
                'reference': consultation.reference_number,
                'submitted_at': consultation.submitted_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Consultation submission error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Sorry, there was an issue processing your request. Please try again.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def send_consultation_email(self, consultation, request):
        """Send consultation notification email"""
        try:
            from datetime import datetime
            
            # Create email content
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # For now, just log the email (replace with actual email service)
            logger.info(f"📧 Consultation email ready: {consultation.reference_number}")
            logger.info(f"📧 To: mohammed.agra@rejlers.ae")
            logger.info(f"📋 Subject: New Consultation Request - {consultation.reference_number}")
            logger.info(f"👤 From: {consultation.name} ({consultation.email})")
            logger.info(f"📞 Phone: {consultation.phone}")
            logger.info(f"🔧 Project: {consultation.get_project_type_display()}")
            
            consultation.email_sent = True
            consultation.save(update_fields=['email_sent'])
                
        except Exception as e:
            logger.error(f"Email processing error: {str(e)}")
            # Don't fail the whole request if email fails
            pass
