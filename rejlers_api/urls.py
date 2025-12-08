"""
URL configuration for Rejlers API system.

Advanced and secure API endpoints for Rejlers engineering consultancy.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from simple_health import health_check, ready_check

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Welcome to Rejlers AI-Powered ERP System for Oil & Gas Engineering',
        'version': 'v1',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'projects': '/api/v1/projects/',
            'services': '/api/v1/services/',
            'team': '/api/v1/team/',
            'ai_erp': '/ai-erp/',
            'drawing_analysis': '/drawing-analysis/',
            'simulation_management': '/simulation-management/',
            'admin': '/admin/',
        },
        'ai_endpoints': {
            'pdf_to_pid_conversion': '/ai-erp/api/ai/pdf-to-pid-conversion/',
            'document_classification': '/ai-erp/api/ai/document-classification/',
            'document_validation': '/ai-erp/api/ai/document-validation/',
            'bulk_processing': '/ai-erp/api/ai/bulk-processing/',
            'service_status': '/ai-erp/api/ai/service-status/'
        },
        'ai_features': {
            'drawing_analysis': 'AI-powered technical drawing analysis with GPT-4 Vision',
            'document_classification': 'Intelligent document type classification and processing',
            'document_validation': 'Comprehensive AI-powered document validation',
            'bulk_processing': 'Batch document processing with OpenAI integration',
            'simulation_assistance': 'AI-assisted engineering simulations',
            'engineering_guidance': 'Domain-specific AI engineering assistance'
        },
        'documentation': '/api/v1/docs/',
        'health': '/api/v1/auth/health/'
    })

urlpatterns = [
    # Railway health checks - multiple paths
    path('', health_check, name='root'),
    path('health/', health_check, name='health'), 
    path('api/v1/health/', health_check, name='api_health'),
    path('api/v1/ready/', ready_check, name='ready'),
    path('ping/', health_check, name='ping'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API root
    path('api/v1/', api_root, name='api_root'),
    
    # API endpoints
    path('api/v1/auth/', include('authentication.api_urls')),
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/services/', include('services.urls')),
    path('api/v1/team/', include('team.urls')),
    
    # AI ERP System
    path('ai-erp/', include('ai_erp.urls')),
    path('drawing-analysis/', include('drawing_analysis.urls')),
    path('simulation-management/', include('simulation_management.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
