"""
URL patterns for Drawing Analysis App
AI-powered technical drawing analysis and management
"""

from django.urls import path
from . import views

app_name = 'drawing_analysis'

urlpatterns = [
    # Drawing management
    path('drawings/', views.drawing_list, name='drawing_list'),
    path('drawings/<int:drawing_id>/', views.drawing_detail, name='drawing_detail'),
    path('upload/', views.upload_drawing, name='upload_drawing'),
    path('upload/<int:project_id>/', views.upload_drawing, name='upload_drawing_project'),
    
    # AI Analysis
    path('drawings/<int:drawing_id>/analyze/', views.analyze_drawing, name='analyze_drawing'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    
    # Comments and Versions
    path('drawings/<int:drawing_id>/comment/', views.add_comment, name='add_comment'),
    path('drawings/<int:drawing_id>/version/', views.create_version, name='create_version'),
]