from django.urls import path, include
from . import views

app_name = 'projects'

# Category URLs
category_patterns = [
    path('', views.ProjectCategoryListView.as_view(), name='category-list'),
    path('<slug:slug>/', views.ProjectCategoryDetailView.as_view(), name='category-detail'),
]

# Technology URLs
technology_patterns = [
    path('', views.ProjectTechnologyListView.as_view(), name='technology-list'),
    path('<uuid:pk>/', views.ProjectTechnologyDetailView.as_view(), name='technology-detail'),
]

# Project-specific URLs (nested under projects)
project_nested_patterns = [
    # Project images
    path('<slug:project_slug>/images/', views.ProjectImageListCreateView.as_view(), name='project-images'),
    path('<slug:project_slug>/images/<uuid:pk>/', views.ProjectImageDetailView.as_view(), name='project-image-detail'),
    
    # Project milestones
    path('<slug:project_slug>/milestones/', views.ProjectMilestoneListCreateView.as_view(), name='project-milestones'),
    path('<slug:project_slug>/milestones/<uuid:pk>/', views.ProjectMilestoneDetailView.as_view(), name='project-milestone-detail'),
    
    # Project technologies
    path('<slug:project_slug>/technologies/', views.ProjectTechnologyUsageView.as_view(), name='project-technologies'),
]

# Main URL patterns
urlpatterns = [
    # Project categories
    path('categories/', include(category_patterns)),
    
    # Technologies
    path('technologies/', include(technology_patterns)),
    
    # Projects
    path('', views.ProjectListView.as_view(), name='project-list'),
    path('featured/', views.FeaturedProjectsView.as_view(), name='featured-projects'),
    path('stats/', views.project_stats_view, name='project-stats'),
    path('public-stats/', views.public_project_stats_view, name='public-project-stats'),
    path('search-options/', views.project_search_options_view, name='search-options'),
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Nested project URLs
    path('', include(project_nested_patterns)),
]