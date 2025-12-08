"""
Simulation Management Views for Oil & Gas ERP System
Engineering simulation management and AI assistance
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.conf import settings
import json
import logging
from datetime import datetime, timedelta

from .models import SimulationProject, SimulationModel, SimulationRun, SimulationResult, AISimulationAssistant
from projects.models import Project
# Temporarily comment out to allow migrations
# from ai_erp.rbac import require_role, require_permissions
# from ai_erp.ai_services import AISimulationAssistant as AISimAssistant
from ai_erp.models import AISystemLog

logger = logging.getLogger(__name__)

#@require_permissions(['view_simulations'])
def simulation_list(request):
    """List all simulation projects with filtering"""
    
    simulations = SimulationProject.objects.select_related('created_by', 'assigned_engineer', 'project').all()
    
    # Apply filters
    project_filter = request.GET.get('project')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')
    
    if project_filter:
        simulations = simulations.filter(project_id=project_filter)
    
    if type_filter:
        simulations = simulations.filter(simulation_type=type_filter)
    
    if status_filter:
        simulations = simulations.filter(status=status_filter)
    
    if priority_filter:
        simulations = simulations.filter(priority=priority_filter)
    
    if search_query:
        simulations = simulations.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(simulation_parameters__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(simulations, 20)
    page = request.GET.get('page')
    simulations_page = paginator.get_page(page)
    
    # Get filter options
    projects = Project.objects.all()
    simulation_types = SimulationProject.SIMULATION_TYPES
    priorities = SimulationProject.PRIORITY_CHOICES
    
    context = {
        'simulations': simulations_page,
        'projects': projects,
        'simulation_types': simulation_types,
        'priorities': priorities,
        'filters': {
            'project': project_filter,
            'type': type_filter,
            'status': status_filter,
            'priority': priority_filter,
            'search': search_query
        },
        'page_title': 'Simulation Projects'
    }
    
    return render(request, 'simulation_management/simulation_list.html', context)

#@require_permissions(['create_simulations'])
@require_http_methods(['GET', 'POST'])
def create_simulation(request, project_id=None):
    """Create new simulation project"""
    
    if request.method == 'POST':
        return handle_simulation_creation(request, project_id)
    
    # GET request - show creation form
    projects = Project.objects.all() if not project_id else Project.objects.filter(id=project_id)
    
    context = {
        'projects': projects,
        'selected_project': project_id,
        'simulation_types': SimulationProject.SIMULATION_TYPES,
        'priorities': SimulationProject.PRIORITY_CHOICES,
        'page_title': 'Create Simulation Project'
    }
    
    return render(request, 'simulation_management/create_simulation.html', context)

def handle_simulation_creation(request, project_id):
    """Handle simulation project creation"""
    
    try:
        # Get form data
        project_id = request.POST.get('project') or project_id
        name = request.POST.get('name')
        simulation_type = request.POST.get('simulation_type')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        assigned_engineer_id = request.POST.get('assigned_engineer')
        
        # Validate required fields
        if not all([project_id, name, simulation_type]):
            return JsonResponse({'error': 'All required fields must be provided'}, status=400)
        
        # Get project
        project = get_object_or_404(Project, id=project_id)
        
        # Get assigned engineer if provided
        assigned_engineer = None
        if assigned_engineer_id:
            from authentication.models import RejlersUser
            assigned_engineer = get_object_or_404(RejlersUser, id=assigned_engineer_id)
        
        # Parse simulation parameters
        simulation_parameters = {}
        for key in request.POST.keys():
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                simulation_parameters[param_name] = request.POST.get(key)
        
        # Create simulation project
        simulation = SimulationProject.objects.create(
            project=project,
            created_by=request.user,
            assigned_engineer=assigned_engineer,
            name=name,
            simulation_type=simulation_type,
            description=description,
            priority=priority,
            simulation_parameters=simulation_parameters,
            status='setup'
        )
        
        # Log the creation
        AISystemLog.objects.create(
            user=request.user,
            log_type='simulation_created',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'simulation_id': simulation.id,
                'simulation_name': name,
                'simulation_type': simulation_type,
                'project_id': project_id
            },
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Simulation project created successfully',
            'simulation_id': simulation.id,
            'redirect_url': f'/simulation-management/simulations/{simulation.id}/'
        })
        
    except Exception as e:
        logger.error(f"Failed to create simulation: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['view_simulations'])
def simulation_detail(request, simulation_id):
    """Simulation project detail view"""
    
    simulation = get_object_or_404(SimulationProject, id=simulation_id)
    
    # Check access permissions
    if not can_access_simulation(request.user, simulation):
        raise Http404("Simulation not found")
    
    # Get simulation runs
    runs = SimulationRun.objects.filter(simulation=simulation).order_by('-created_at')
    
    # Get AI assistance history
    ai_assistance = AISimulationAssistant.objects.filter(simulation=simulation).order_by('-created_at')
    
    # Get simulation models
    models = SimulationModel.objects.filter(simulation=simulation).order_by('-created_at')
    
    # Check permissions
    can_run = request.user.erp_profile.role.permissions.get('run_simulations', False) if hasattr(request.user, 'erp_profile') else False
    can_edit = request.user.erp_profile.role.permissions.get('manage_simulations', False) if hasattr(request.user, 'erp_profile') else False
    can_ai_assist = request.user.erp_profile.role.permissions.get('ai_assistance', False) if hasattr(request.user, 'erp_profile') else False
    
    context = {
        'simulation': simulation,
        'runs': runs,
        'ai_assistance': ai_assistance,
        'models': models,
        'can_run': can_run,
        'can_edit': can_edit,
        'can_ai_assist': can_ai_assist,
        'page_title': f'Simulation: {simulation.name}'
    }
    
    return render(request, 'simulation_management/simulation_detail.html', context)

#@require_permissions(['run_simulations'])
@require_http_methods(['POST'])
def run_simulation(request, simulation_id):
    """Start simulation run"""
    
    try:
        simulation = get_object_or_404(SimulationProject, id=simulation_id)
        
        # Check if simulation is ready to run
        if simulation.status not in ['setup', 'completed', 'failed']:
            return JsonResponse({
                'error': 'Simulation is not ready to run'
            }, status=400)
        
        # Get run parameters
        run_name = request.POST.get('run_name', f'Run {timezone.now().strftime("%Y%m%d_%H%M%S")}')
        run_parameters = {}
        
        for key in request.POST.keys():
            if key.startswith('run_param_'):
                param_name = key.replace('run_param_', '')
                run_parameters[param_name] = request.POST.get(key)
        
        # Create simulation run
        run = SimulationRun.objects.create(
            simulation=simulation,
            started_by=request.user,
            run_name=run_name,
            run_parameters=run_parameters,
            status='running'
        )
        
        # Update simulation status
        simulation.status = 'running'
        simulation.save()
        
        # Log the run start
        AISystemLog.objects.create(
            user=request.user,
            log_type='simulation_run',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'simulation_id': simulation.id,
                'run_id': run.id,
                'run_name': run_name
            },
            success=True
        )
        
        # TODO: Integrate with actual simulation execution system
        # For now, we'll simulate the process
        
        return JsonResponse({
            'success': True,
            'message': 'Simulation run started successfully',
            'run_id': run.id
        })
        
    except Exception as e:
        logger.error(f"Failed to start simulation run: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['ai_assistance'])
@require_http_methods(['POST'])
def get_ai_assistance(request, simulation_id):
    """Get AI assistance for simulation"""
    
    try:
        simulation = get_object_or_404(SimulationProject, id=simulation_id)
        assistance_type = request.POST.get('assistance_type')
        question = request.POST.get('question', '')
        
        if not assistance_type:
            return JsonResponse({'error': 'Assistance type is required'}, status=400)
        
        # Initialize AI assistant
        ai_assistant = AISimAssistant()
        
        start_time = timezone.now()
        
        # Get AI assistance
        assistance_result = ai_assistant.get_simulation_assistance(
            simulation_type=simulation.simulation_type,
            assistance_type=assistance_type,
            simulation_parameters=simulation.simulation_parameters,
            question=question
        )
        
        processing_time = (timezone.now() - start_time).total_seconds()
        
        # Create assistance record
        assistance = AISimulationAssistant.objects.create(
            simulation=simulation,
            requested_by=request.user,
            assistance_type=assistance_type,
            question=question,
            ai_response=assistance_result.get('response', ''),
            confidence_score=assistance_result.get('confidence', 0.0),
            tokens_used=assistance_result.get('tokens_used', 0),
            processing_time=processing_time
        )
        
        # Log the assistance
        AISystemLog.objects.create(
            user=request.user,
            log_type='ai_assistance',
            ai_model_used=settings.OPENAI_MODEL,
            processing_time=processing_time,
            tokens_used=assistance_result.get('tokens_used', 0),
            input_data={
                'simulation_id': simulation.id,
                'assistance_type': assistance_type,
                'question': question
            },
            output_data=assistance_result,
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'response': assistance_result.get('response', ''),
            'confidence': assistance_result.get('confidence', 0.0),
            'assistance_id': assistance.id
        })
        
    except Exception as e:
        logger.error(f"Failed to get AI assistance: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['view_simulations'])
def run_detail(request, run_id):
    """Simulation run detail view"""
    
    run = get_object_or_404(SimulationRun, id=run_id)
    
    # Check access permissions
    if not can_access_simulation(request.user, run.simulation):
        raise Http404("Simulation run not found")
    
    # Get results
    results = SimulationResult.objects.filter(run=run).order_by('-created_at')
    
    context = {
        'run': run,
        'results': results,
        'page_title': f'Run: {run.run_name}'
    }
    
    return render(request, 'simulation_management/run_detail.html', context)

#@require_permissions(['manage_simulations'])
@require_http_methods(['POST'])
def update_simulation_status(request, simulation_id):
    """Update simulation status"""
    
    try:
        simulation = get_object_or_404(SimulationProject, id=simulation_id)
        new_status = request.POST.get('status')
        
        if new_status not in dict(SimulationProject.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        old_status = simulation.status
        simulation.status = new_status
        simulation.save()
        
        # Log the status change
        AISystemLog.objects.create(
            user=request.user,
            log_type='simulation_status_update',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'simulation_id': simulation.id,
                'old_status': old_status,
                'new_status': new_status
            },
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status}'
        })
        
    except Exception as e:
        logger.error(f"Failed to update simulation status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['view_simulations'])
def simulation_dashboard(request):
    """Simulation dashboard overview"""
    
    # Get user's accessible simulations
    if request.user.erp_profile.role.code == 'SUPER_ADMIN':
        simulations = SimulationProject.objects.all()
    else:
        simulations = SimulationProject.objects.filter(
            Q(created_by=request.user) |
            Q(assigned_engineer=request.user) |
            Q(project__in=request.user.projects.all())
        )
    
    # Get statistics
    stats = {
        'total_simulations': simulations.count(),
        'running_simulations': simulations.filter(status='running').count(),
        'completed_simulations': simulations.filter(status='completed').count(),
        'failed_simulations': simulations.filter(status='failed').count(),
        
        'by_type': dict(simulations.values('simulation_type').annotate(count=Count('id')).values_list('simulation_type', 'count')),
        'by_priority': dict(simulations.values('priority').annotate(count=Count('id')).values_list('priority', 'count'))
    }
    
    # Recent activities
    recent_simulations = simulations.order_by('-created_at')[:10]
    recent_runs = SimulationRun.objects.filter(
        simulation__in=simulations
    ).select_related('simulation', 'started_by').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_simulations': recent_simulations,
        'recent_runs': recent_runs,
        'page_title': 'Simulation Dashboard'
    }
    
    return render(request, 'simulation_management/dashboard.html', context)

# Utility functions

def can_access_simulation(user, simulation):
    """Check if user can access simulation"""
    # Super admin can access all
    if hasattr(user, 'erp_profile') and user.erp_profile.role.code == 'SUPER_ADMIN':
        return True
    
    # Simulation creator can access
    if simulation.created_by == user:
        return True
    
    # Assigned engineer can access
    if simulation.assigned_engineer == user:
        return True
    
    # Project members can access
    if simulation.project in user.projects.all():
        return True
    
    return False
