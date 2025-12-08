"""
Drawing Analysis Views for Oil & Gas ERP System
AI-powered technical drawing analysis and management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings
import json
import logging
import os
from datetime import datetime, timedelta

from .models import DrawingDocument, AIDrawingAnalysis, DrawingComment, DrawingVersion
from projects.models import Project
# Temporarily comment out to allow migrations
# from ai_erp.rbac import require_role, require_permissions
# from ai_erp.ai_services import AIDrawingAnalyzer
from ai_erp.models import AISystemLog

logger = logging.getLogger(__name__)

#@require_permissions(['view_drawings'])
def drawing_list(request):
    """List all drawings with filtering and search"""
    
    drawings = DrawingDocument.objects.select_related('project', 'uploaded_by').all()
    
    # Apply filters
    project_filter = request.GET.get('project')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if project_filter:
        drawings = drawings.filter(project_id=project_filter)
    
    if type_filter:
        drawings = drawings.filter(drawing_type=type_filter)
    
    if status_filter:
        drawings = drawings.filter(status=status_filter)
    
    if search_query:
        drawings = drawings.filter(
            Q(title__icontains=search_query) |
            Q(drawing_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(drawings, 20)
    page = request.GET.get('page')
    drawings_page = paginator.get_page(page)
    
    # Get filter options
    projects = Project.objects.all()
    drawing_types = DrawingDocument.DRAWING_TYPES
    
    context = {
        'drawings': drawings_page,
        'projects': projects,
        'drawing_types': drawing_types,
        'filters': {
            'project': project_filter,
            'type': type_filter,
            'status': status_filter,
            'search': search_query
        },
        'page_title': 'Drawing Library'
    }
    
    return render(request, 'drawing_analysis/drawing_list.html', context)

#@require_permissions(['upload_drawings'])
@require_http_methods(['GET', 'POST'])
def upload_drawing(request, project_id=None):
    """Upload new drawing"""
    
    if request.method == 'POST':
        return handle_drawing_upload(request, project_id)
    
    # GET request - show upload form
    projects = Project.objects.all() if not project_id else Project.objects.filter(id=project_id)
    
    context = {
        'projects': projects,
        'selected_project': project_id,
        'drawing_types': DrawingDocument.DRAWING_TYPES,
        'page_title': 'Upload Drawing'
    }
    
    return render(request, 'drawing_analysis/upload_drawing.html', context)

def handle_drawing_upload(request, project_id):
    """Handle drawing file upload"""
    
    try:
        # Get form data
        project_id = request.POST.get('project') or project_id
        title = request.POST.get('title')
        drawing_number = request.POST.get('drawing_number')
        drawing_type = request.POST.get('drawing_type')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        
        # Validate required fields
        if not all([project_id, title, drawing_number, drawing_type, file]):
            return JsonResponse({'error': 'All required fields must be provided'}, status=400)
        
        # Get project
        project = get_object_or_404(Project, id=project_id)
        
        # Validate file type
        allowed_extensions = ['.pdf', '.dwg', '.dxf', '.png', '.jpg', '.jpeg', '.tiff']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'error': f'File type not supported. Allowed types: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Create drawing document
        drawing = DrawingDocument.objects.create(
            project=project,
            uploaded_by=request.user,
            title=title,
            drawing_number=drawing_number,
            drawing_type=drawing_type,
            description=description,
            file=file,
            file_size=file.size,
            file_format=file_extension[1:].upper()  # Remove dot and uppercase
        )
        
        # Log the upload
        AISystemLog.objects.create(
            user=request.user,
            log_type='drawing_upload',
            ai_model_used='system',
            processing_time=0,
            input_data={
                'drawing_id': drawing.id,
                'drawing_number': drawing_number,
                'project_id': project_id,
                'file_size': file.size
            },
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Drawing uploaded successfully',
            'drawing_id': drawing.id,
            'redirect_url': f'/drawing-analysis/drawings/{drawing.id}/'
        })
        
    except Exception as e:
        logger.error(f"Failed to upload drawing: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['view_drawings'])
def drawing_detail(request, drawing_id):
    """Drawing detail view with analysis history"""
    
    drawing = get_object_or_404(DrawingDocument, id=drawing_id)
    
    # Get AI analyses for this drawing
    analyses = AIDrawingAnalysis.objects.filter(drawing=drawing).order_by('-created_at')
    
    # Get comments
    comments = DrawingComment.objects.filter(drawing=drawing).select_related('created_by').order_by('-created_at')
    
    # Get versions
    versions = DrawingVersion.objects.filter(drawing=drawing).order_by('-version_number')
    
    # Check if user can perform AI analysis
    can_analyze = request.user.erp_profile.role.permissions.get('ai_analysis', False) if hasattr(request.user, 'erp_profile') else False
    
    # Check if user can add comments
    can_comment = request.user.erp_profile.role.permissions.get('add_comments', False) if hasattr(request.user, 'erp_profile') else False
    
    context = {
        'drawing': drawing,
        'analyses': analyses,
        'comments': comments,
        'versions': versions,
        'can_analyze': can_analyze,
        'can_comment': can_comment,
        'page_title': f'Drawing: {drawing.title}'
    }
    
    return render(request, 'drawing_analysis/drawing_detail.html', context)

#@require_permissions(['ai_analysis'])
@require_http_methods(['POST'])
def analyze_drawing(request, drawing_id):
    """Initiate AI analysis of drawing"""
    
    try:
        drawing = get_object_or_404(DrawingDocument, id=drawing_id)
        analysis_type = request.POST.get('analysis_type', 'comprehensive')
        
        # Check if analysis is already in progress
        existing_analysis = AIDrawingAnalysis.objects.filter(
            drawing=drawing,
            status='processing'
        ).first()
        
        if existing_analysis:
            return JsonResponse({
                'error': 'Analysis already in progress for this drawing'
            }, status=400)
        
        # Create analysis record
        analysis = AIDrawingAnalysis.objects.create(
            drawing=drawing,
            initiated_by=request.user,
            analysis_type=analysis_type,
            status='processing'
        )
        
        # Initialize AI analyzer
        analyzer = AIDrawingAnalyzer()
        
        # Perform analysis (this would typically be done asynchronously)
        start_time = timezone.now()
        
        try:
            # Get file path
            file_path = drawing.file.path if drawing.file else None
            
            if not file_path or not os.path.exists(file_path):
                raise Exception("Drawing file not found")
            
            # Perform AI analysis
            analysis_result = analyzer.analyze_drawing(
                file_path=file_path,
                drawing_type=drawing.drawing_type,
                analysis_type=analysis_type
            )
            
            # Calculate processing time
            processing_time = (timezone.now() - start_time).total_seconds()
            
            # Update analysis record
            analysis.status = 'completed'
            analysis.confidence_score = analysis_result.get('confidence_score', 0.0)
            analysis.processing_time = processing_time
            analysis.tokens_consumed = analysis_result.get('tokens_used', 0)
            analysis.analysis_results = analysis_result
            analysis.save()
            
            # Log the analysis
            AISystemLog.objects.create(
                user=request.user,
                log_type='drawing_analysis',
                ai_model_used=settings.OPENAI_VISION_MODEL,
                processing_time=processing_time,
                tokens_used=analysis_result.get('tokens_used', 0),
                input_data={
                    'drawing_id': drawing.id,
                    'analysis_type': analysis_type,
                    'drawing_number': drawing.drawing_number
                },
                output_data=analysis_result,
                success=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Analysis completed successfully',
                'analysis_id': analysis.id,
                'confidence_score': analysis.confidence_score,
                'processing_time': processing_time
            })
            
        except Exception as analysis_error:
            # Update analysis record with error
            analysis.status = 'failed'
            analysis.error_message = str(analysis_error)
            analysis.save()
            
            # Log the failed analysis
            AISystemLog.objects.create(
                user=request.user,
                log_type='drawing_analysis',
                ai_model_used=settings.OPENAI_VISION_MODEL,
                processing_time=(timezone.now() - start_time).total_seconds(),
                input_data={
                    'drawing_id': drawing.id,
                    'analysis_type': analysis_type
                },
                error_message=str(analysis_error),
                success=False
            )
            
            raise analysis_error
            
    except Exception as e:
        logger.error(f"Failed to analyze drawing: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['view_drawings'])
def analysis_detail(request, analysis_id):
    """View detailed analysis results"""
    
    analysis = get_object_or_404(AIDrawingAnalysis, id=analysis_id)
    
    # Check if user has access to this analysis
    if not can_access_analysis(request.user, analysis):
        raise Http404("Analysis not found")
    
    context = {
        'analysis': analysis,
        'page_title': f'Analysis Results: {analysis.drawing.title}'
    }
    
    return render(request, 'drawing_analysis/analysis_detail.html', context)

#@require_permissions(['add_comments'])
@require_http_methods(['POST'])
def add_comment(request, drawing_id):
    """Add comment to drawing"""
    
    try:
        drawing = get_object_or_404(DrawingDocument, id=drawing_id)
        comment_text = request.POST.get('comment', '').strip()
        x_coordinate = request.POST.get('x_coordinate')
        y_coordinate = request.POST.get('y_coordinate')
        
        if not comment_text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        
        # Create comment
        comment = DrawingComment.objects.create(
            drawing=drawing,
            created_by=request.user,
            comment=comment_text,
            x_coordinate=float(x_coordinate) if x_coordinate else None,
            y_coordinate=float(y_coordinate) if y_coordinate else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Comment added successfully',
            'comment': {
                'id': comment.id,
                'comment': comment.comment,
                'author': comment.created_by.get_full_name() or comment.created_by.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to add comment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

#@require_permissions(['manage_drawings'])
@require_http_methods(['POST'])
def create_version(request, drawing_id):
    """Create new version of drawing"""
    
    try:
        drawing = get_object_or_404(DrawingDocument, id=drawing_id)
        version_notes = request.POST.get('notes', '')
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({'error': 'File is required for new version'}, status=400)
        
        # Get next version number
        latest_version = DrawingVersion.objects.filter(drawing=drawing).order_by('-version_number').first()
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        # Create new version
        version = DrawingVersion.objects.create(
            drawing=drawing,
            version_number=next_version,
            file=file,
            created_by=request.user,
            version_notes=version_notes
        )
        
        # Update drawing's current version
        drawing.current_version = next_version
        drawing.file = file  # Update to latest file
        drawing.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Version {next_version} created successfully',
            'version_id': version.id
        })
        
    except Exception as e:
        logger.error(f"Failed to create version: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Utility functions

def can_access_analysis(user, analysis):
    """Check if user can access analysis"""
    # Super admin can access all
    if user.erp_profile.role.code == 'SUPER_ADMIN':
        return True
    
    # Users can access their own analyses
    if analysis.initiated_by == user:
        return True
    
    # Project members can access project analyses
    if analysis.drawing.project in user.projects.all():
        return True
    
    return False
