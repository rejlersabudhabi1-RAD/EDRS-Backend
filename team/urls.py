from django.urls import path, include
from . import views

app_name = 'team'

# Department URLs
department_patterns = [
    path('', views.DepartmentListView.as_view(), name='department-list'),
    path('<slug:slug>/', views.DepartmentDetailView.as_view(), name='department-detail'),
]

# Position URLs
position_patterns = [
    path('', views.PositionListView.as_view(), name='position-list'),
    path('<slug:slug>/', views.PositionDetailView.as_view(), name='position-detail'),
]

# Skill Category URLs
skill_category_patterns = [
    path('', views.SkillCategoryListView.as_view(), name='skill-category-list'),
    path('<uuid:pk>/', views.SkillCategoryDetailView.as_view(), name='skill-category-detail'),
]

# Skill URLs
skill_patterns = [
    path('', views.SkillListView.as_view(), name='skill-list'),
    path('<uuid:pk>/', views.SkillDetailView.as_view(), name='skill-detail'),
]

# Team Project URLs
project_patterns = [
    path('', views.TeamProjectListView.as_view(), name='project-list'),
    path('<uuid:pk>/', views.TeamProjectDetailView.as_view(), name='project-detail'),
]

# Team Member nested URLs (member-specific resources)
member_nested_patterns = [
    # Member skills
    path('<uuid:member_id>/skills/', views.TeamMemberSkillListCreateView.as_view(), name='member-skills'),
    path('<uuid:member_id>/skills/<uuid:pk>/', views.TeamMemberSkillDetailView.as_view(), name='member-skill-detail'),
    
    # Member education
    path('<uuid:member_id>/education/', views.EducationListCreateView.as_view(), name='member-education'),
    path('<uuid:member_id>/education/<uuid:pk>/', views.EducationDetailView.as_view(), name='member-education-detail'),
    
    # Member certifications
    path('<uuid:member_id>/certifications/', views.CertificationListCreateView.as_view(), name='member-certifications'),
    path('<uuid:member_id>/certifications/<uuid:pk>/', views.CertificationDetailView.as_view(), name='member-certification-detail'),
    
    # Member project assignments
    path('<uuid:member_id>/projects/', views.TeamMemberProjectListCreateView.as_view(), name='member-projects'),
    path('<uuid:member_id>/projects/<uuid:pk>/', views.TeamMemberProjectDetailView.as_view(), name='member-project-detail'),
    
    # Member achievements
    path('<uuid:member_id>/achievements/', views.AchievementListCreateView.as_view(), name='member-achievements'),
    path('<uuid:member_id>/achievements/<uuid:pk>/', views.AchievementDetailView.as_view(), name='member-achievement-detail'),
]

# Main URL patterns
urlpatterns = [
    # Departments
    path('departments/', include(department_patterns)),
    
    # Positions
    path('positions/', include(position_patterns)),
    
    # Skill categories
    path('skill-categories/', include(skill_category_patterns)),
    
    # Skills
    path('skills/', include(skill_patterns)),
    
    # Team projects
    path('projects/', include(project_patterns)),
    
    # Team members
    path('members/', views.TeamMemberListView.as_view(), name='member-list'),
    path('members/featured/', views.FeaturedTeamMembersView.as_view(), name='featured-members'),
    path('members/stats/', views.team_stats_view, name='team-stats'),
    path('members/public-stats/', views.public_team_stats_view, name='public-team-stats'),
    path('members/search-options/', views.team_search_options_view, name='search-options'),
    path('members/<uuid:pk>/', views.TeamMemberDetailView.as_view(), name='member-detail'),
    
    # Nested member URLs
    path('members/', include(member_nested_patterns)),
]