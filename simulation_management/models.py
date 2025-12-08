from django.db import models
from authentication.models import RejlersUser
from drawing_analysis.models import DrawingDocument
import uuid
from django.core.validators import FileExtensionValidator

class SimulationProject(models.Model):
    """Simulation projects for engineering analysis"""
    SIMULATION_TYPES = [
        ('cfd', 'Computational Fluid Dynamics'),
        ('fea', 'Finite Element Analysis'),
        ('thermal', 'Thermal Analysis'),
        ('stress', 'Stress Analysis'),
        ('flow', 'Flow Simulation'),
        ('pressure', 'Pressure Analysis'),
        ('vibration', 'Vibration Analysis'),
        ('fatigue', 'Fatigue Analysis'),
        ('corrosion', 'Corrosion Modeling'),
        ('reservoir', 'Reservoir Simulation'),
        ('wellbore', 'Wellbore Analysis'),
        ('pipeline', 'Pipeline Simulation'),
        ('safety', 'Safety Analysis'),
        ('environmental', 'Environmental Impact'),
        ('optimization', 'Process Optimization'),
    ]
    
    STATUS_CHOICES = [
        ('setup', 'Setup'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='simulations')
    created_by = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='created_simulations')
    assigned_engineer = models.ForeignKey(RejlersUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_simulations')
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField()
    simulation_type = models.CharField(max_length=20, choices=SIMULATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    # Technical Parameters
    software_used = models.CharField(max_length=100, help_text="Simulation software/tool")
    version = models.CharField(max_length=50, blank=True)
    license_required = models.CharField(max_length=100, blank=True)
    
    # Resource Requirements
    estimated_runtime = models.DurationField(help_text="Expected simulation runtime")
    cpu_hours_estimated = models.FloatField(help_text="Estimated CPU hours")
    memory_required_gb = models.PositiveIntegerField(help_text="Required memory in GB")
    storage_required_gb = models.PositiveIntegerField(help_text="Required storage in GB")
    
    # Status and Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='setup')
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Timing
    planned_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    planned_completion = models.DateTimeField()
    actual_completion = models.DateTimeField(null=True, blank=True)
    
    # AI Enhancement
    ai_assisted = models.BooleanField(default=False)
    ai_recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'simulation_project'
        verbose_name = 'Simulation Project'
        verbose_name_plural = 'Simulation Projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.simulation_type})"

class SimulationModel(models.Model):
    """3D models and input files for simulation"""
    MODEL_TYPES = [
        ('cad', 'CAD Model'),
        ('mesh', 'Mesh Model'),
        ('geometry', 'Geometry File'),
        ('input', 'Input File'),
        ('boundary', 'Boundary Conditions'),
        ('material', 'Material Properties'),
        ('loads', 'Load Definition'),
        ('constraints', 'Constraints'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(SimulationProject, on_delete=models.CASCADE, related_name='models')
    source_drawing = models.ForeignKey(DrawingDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='simulation_models')
    
    # Model Information
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    
    # File Details
    file = models.FileField(
        upload_to='simulation_models/%Y/%m/',
        validators=[FileExtensionValidator(['step', 'iges', 'dwg', 'dxf', 'stl', 'obj', 'inp', 'msh', 'dat'])]
    )
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    
    # Model Properties
    units = models.CharField(max_length=20, default='mm')
    scale_factor = models.FloatField(default=1.0)
    coordinate_system = models.CharField(max_length=50, default='cartesian')
    
    # Processing Status
    processed = models.BooleanField(default=False)
    processing_log = models.TextField(blank=True)
    
    # AI Generated
    ai_generated = models.BooleanField(default=False)
    ai_model_used = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'simulation_model'
        verbose_name = 'Simulation Model'
        verbose_name_plural = 'Simulation Models'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.model_type}"

class SimulationRun(models.Model):
    """Individual simulation run execution"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(SimulationProject, on_delete=models.CASCADE, related_name='runs')
    run_number = models.PositiveIntegerField()
    
    # Run Configuration
    parameters = models.JSONField(default=dict, help_text="Simulation parameters")
    boundary_conditions = models.JSONField(default=dict)
    material_properties = models.JSONField(default=dict)
    
    # Execution Details
    started_by = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='started_runs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Resource Usage
    cpu_time_used = models.FloatField(null=True, blank=True, help_text="CPU hours used")
    memory_used_gb = models.FloatField(null=True, blank=True)
    
    # Results
    status = models.CharField(max_length=20, choices=SimulationProject.STATUS_CHOICES, default='setup')
    convergence_achieved = models.BooleanField(null=True, blank=True)
    iterations_completed = models.PositiveIntegerField(null=True, blank=True)
    
    # Output Files
    results_file = models.FileField(upload_to='simulation_results/%Y/%m/', blank=True)
    log_file = models.FileField(upload_to='simulation_logs/%Y/%m/', blank=True)
    
    # Error Handling
    error_message = models.TextField(blank=True)
    warnings = models.JSONField(default=list)
    
    class Meta:
        db_table = 'simulation_run'
        verbose_name = 'Simulation Run'
        verbose_name_plural = 'Simulation Runs'
        unique_together = ['simulation', 'run_number']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.simulation.name} - Run {self.run_number}"

class SimulationResult(models.Model):
    """Results and analysis from simulation runs"""
    RESULT_TYPES = [
        ('stress', 'Stress Results'),
        ('displacement', 'Displacement Results'),
        ('temperature', 'Temperature Results'),
        ('pressure', 'Pressure Results'),
        ('velocity', 'Velocity Results'),
        ('flow_rate', 'Flow Rate Results'),
        ('safety_factor', 'Safety Factor'),
        ('fatigue_life', 'Fatigue Life'),
        ('frequency', 'Frequency Analysis'),
        ('buckling', 'Buckling Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(SimulationRun, on_delete=models.CASCADE, related_name='results')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPES)
    
    # Result Data
    max_value = models.FloatField()
    min_value = models.FloatField()
    average_value = models.FloatField()
    units = models.CharField(max_length=50)
    
    # Location Information
    max_location = models.JSONField(default=dict, help_text="Coordinates of maximum value")
    min_location = models.JSONField(default=dict, help_text="Coordinates of minimum value")
    
    # Analysis
    within_limits = models.BooleanField(null=True, blank=True)
    safety_margin = models.FloatField(null=True, blank=True)
    design_criteria = models.JSONField(default=dict)
    
    # AI Analysis
    ai_analysis = models.TextField(blank=True)
    ai_recommendations = models.JSONField(default=list)
    risk_assessment = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ], blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'simulation_result'
        verbose_name = 'Simulation Result'
        verbose_name_plural = 'Simulation Results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.run} - {self.result_type}"

class AISimulationAssistant(models.Model):
    """AI assistant for simulation setup and optimization"""
    ASSISTANCE_TYPES = [
        ('parameter_optimization', 'Parameter Optimization'),
        ('mesh_recommendations', 'Mesh Recommendations'),
        ('boundary_conditions', 'Boundary Conditions Setup'),
        ('material_selection', 'Material Selection'),
        ('convergence_help', 'Convergence Assistance'),
        ('result_interpretation', 'Result Interpretation'),
        ('design_optimization', 'Design Optimization'),
        ('failure_analysis', 'Failure Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(SimulationProject, on_delete=models.CASCADE, related_name='ai_assistance')
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='simulation_ai_sessions')
    assistance_type = models.CharField(max_length=30, choices=ASSISTANCE_TYPES)
    
    # AI Session
    query = models.TextField()
    response = models.TextField()
    ai_model_used = models.CharField(max_length=100)
    tokens_used = models.PositiveIntegerField(default=0)
    
    # Context
    context_data = models.JSONField(default=dict)
    recommendations_applied = models.BooleanField(default=False)
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_simulation_assistant'
        verbose_name = 'AI Simulation Assistant'
        verbose_name_plural = 'AI Simulation Assistant Sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.simulation.name} - {self.assistance_type}"
