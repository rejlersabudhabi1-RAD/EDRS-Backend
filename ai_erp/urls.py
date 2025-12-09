"""
URL patterns for AI ERP System
Super Admin Dashboard and Management URLs
"""

from django.urls import path, include
from . import views
from . import dashboard_views
from . import ai_views

app_name = 'ai_erp'

urlpatterns = [
    # Dashboard routing
    path('', dashboard_views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/', dashboard_views.role_dashboard, name='role_dashboard'),
    
    # Super Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # AI-Powered User Management
    path('users/', views.user_management, name='user_management'),
    path('users/ai-management/', views.ai_user_management, name='ai_user_management'),
    path('users/update-role/<int:user_id>/', views.update_user_role, name='update_user_role'),
    
    # Real-time Monitoring
    path('monitoring/activity/', views.real_time_activity_monitor, name='real_time_activity'),
    
    # AI System Analytics
    path('analytics/ai-insights/', views.ai_system_analytics, name='ai_system_analytics'),
    
    # Role Management
    path('roles/', views.role_management, name='role_management'),
    
    # Project Oversight
    path('projects/', views.project_oversight, name='project_oversight'),
    
    # AI System Monitoring  
    path('system-monitoring/', views.ai_system_monitoring, name='system_monitoring'),
    
    # AWS Integration API
    path('api/aws-test/', views.AWSConnectionTestView.as_view(), name='aws_test'),
    path('api/aws-status/', views.AWSStatusView.as_view(), name='aws_status'),
    path('api/aws-send-email/', views.AWSSendTestEmailView.as_view(), name='aws_send_email'),
    path('ai-monitoring/', views.ai_system_monitoring, name='ai_monitoring'),
    
    # Drawing Analysis Overview
    path('drawings/', views.drawing_analysis_overview, name='drawing_overview'),
    
    # Simulation System Overview
    path('simulations/', views.simulation_system_overview, name='simulation_overview'),
    
    # System Configuration
    path('config/', views.system_configuration, name='system_configuration'),
    
    # AI-Enhanced EDRS Platform Endpoints
    
    # PDF to P&ID Conversion with OpenAI Vision
    path('api/ai/pdf-to-pid-conversion/', 
         ai_views.PDFToPIDConversionAPI.as_view(), 
         name='pdf_to_pid_conversion'),
    
    # Document Classification with OpenAI
    path('api/ai/document-classification/', 
         ai_views.DocumentClassificationAPI.as_view(), 
         name='document_classification'),
    
    # Document Validation with AI Analysis
    path('api/ai/document-validation/', 
         ai_views.DocumentValidationAPI.as_view(), 
         name='document_validation'),
    
    # Bulk Document Processing
    path('api/ai/bulk-processing/', 
         ai_views.BulkDocumentProcessingAPI.as_view(), 
         name='bulk_document_processing'),
    
    # Document Upload with Report Generation
    path('api/ai/document-upload-report/', 
         ai_views.DocumentUploadWithReportAPI.as_view(), 
         name='document_upload_report'),
    
    # AI Service Status and Health Check
    path('api/ai/service-status/', 
         ai_views.AIServiceStatusAPI.as_view(), 
         name='ai_service_status'),
    
    # Enhanced User Management API
    path('api/users/features/', views.get_feature_permissions, name='get_feature_permissions'),
    path('api/users/create/', views.create_user_with_permissions, name='create_user_with_permissions'),
    path('api/users/<uuid:user_id>/permissions/', views.get_user_permissions, name='get_user_permissions'),
    
    # Consultation Form API
    path('api/consultation/submit/', views.ConsultationSubmissionAPI.as_view(), name='consultation_submit'),
]