"""
URL patterns for Simulation Management App
Engineering simulation management and AI assistance
"""

from django.urls import path
from . import views

app_name = 'simulation_management'

urlpatterns = [
    # Simulation dashboard
    path('', views.simulation_dashboard, name='dashboard'),
    
    # Simulation project management
    path('simulations/', views.simulation_list, name='simulation_list'),
    path('simulations/<int:simulation_id>/', views.simulation_detail, name='simulation_detail'),
    path('create/', views.create_simulation, name='create_simulation'),
    path('create/<int:project_id>/', views.create_simulation, name='create_simulation_project'),
    
    # Simulation operations
    path('simulations/<int:simulation_id>/run/', views.run_simulation, name='run_simulation'),
    path('simulations/<int:simulation_id>/status/', views.update_simulation_status, name='update_status'),
    path('simulations/<int:simulation_id>/ai-assist/', views.get_ai_assistance, name='ai_assistance'),
    
    # Simulation runs
    path('runs/<int:run_id>/', views.run_detail, name='run_detail'),
]