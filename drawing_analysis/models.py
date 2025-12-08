from django.db import models
from authentication.models import RejlersUser
from ai_erp.models import ProjectERPInfo
import uuid
from django.core.validators import FileExtensionValidator
import os

class DrawingDocument(models.Model):
    """Technical drawing documents for analysis"""
    DRAWING_TYPES = [
        ('pid', 'Piping & Instrumentation Diagram'),
        ('pfd', 'Process Flow Diagram'),
        ('ga', 'General Arrangement'),
        ('isometric', 'Isometric Drawing'),
        ('plan', 'Plan View'),
        ('section', 'Section View'),
        ('detail', 'Detail Drawing'),
        ('schematic', 'Schematic Diagram'),
        ('electrical', 'Electrical Drawing'),
        ('mechanical', 'Mechanical Drawing'),
        ('structural', 'Structural Drawing'),
        ('hvac', 'HVAC Drawing'),
        ('firewater', 'Fire & Safety Systems'),
        ('layout', 'Equipment Layout'),
        ('plot_plan', 'Plot Plan'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='drawings')
    uploaded_by = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='uploaded_drawings')
    
    # File Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    drawing_number = models.CharField(max_length=100, unique=True)
    revision = models.CharField(max_length=10, default='A')
    drawing_type = models.CharField(max_length=20, choices=DRAWING_TYPES)
    
    # File Details
    file = models.FileField(
        upload_to='drawings/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'dwg', 'dxf'])]
    )
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_format = models.CharField(max_length=10)
    
    # Processing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    scale = models.CharField(max_length=50, blank=True)
    units = models.CharField(max_length=20, default='mm')
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drawing_document'
        verbose_name = 'Drawing Document'
        verbose_name_plural = 'Drawing Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.drawing_number} - {self.title}"
    
    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

class AIDrawingAnalysis(models.Model):
    """AI analysis results for technical drawings"""
    ANALYSIS_TYPES = [
        ('text_extraction', 'Text Extraction'),
        ('component_detection', 'Component Detection'),
        ('dimension_analysis', 'Dimension Analysis'),
        ('symbol_recognition', 'Symbol Recognition'),
        ('compliance_check', 'Compliance Check'),
        ('safety_analysis', 'Safety Analysis'),
        ('cost_estimation', 'Cost Estimation'),
        ('material_takeoff', 'Material Take-off'),
        ('clash_detection', 'Clash Detection'),
        ('quality_check', 'Quality Check'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drawing = models.ForeignKey(DrawingDocument, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    initiated_by = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='drawing_analyses')
    
    # AI Model Information
    ai_model_used = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    tokens_consumed = models.PositiveIntegerField(default=0)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    
    # Analysis Results
    extracted_text = models.TextField(blank=True)
    detected_components = models.JSONField(default=list)
    identified_symbols = models.JSONField(default=list)
    dimensions = models.JSONField(default=list)
    materials_list = models.JSONField(default=list)
    
    # Analysis Scores
    confidence_score = models.FloatField(null=True, blank=True)
    accuracy_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)
    
    # Findings and Recommendations
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    safety_concerns = models.JSONField(default=list)
    compliance_issues = models.JSONField(default=list)
    
    # Results
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_drawing_analysis'
        verbose_name = 'AI Drawing Analysis'
        verbose_name_plural = 'AI Drawing Analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.drawing.drawing_number} - {self.analysis_type}"

class DrawingComment(models.Model):
    """Comments and annotations on drawings"""
    COMMENT_TYPES = [
        ('general', 'General Comment'),
        ('revision', 'Revision Request'),
        ('approval', 'Approval Note'),
        ('concern', 'Safety Concern'),
        ('suggestion', 'Improvement Suggestion'),
        ('compliance', 'Compliance Note'),
        ('ai_finding', 'AI Generated Finding'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drawing = models.ForeignKey(DrawingDocument, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='drawing_comments')
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='general')
    
    # Comment Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    coordinates = models.JSONField(default=dict, help_text="X, Y coordinates on drawing")
    
    # Status and Priority
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(RejlersUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_comments')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # AI Enhancement
    ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drawing_comment'
        verbose_name = 'Drawing Comment'
        verbose_name_plural = 'Drawing Comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.drawing.drawing_number} - {self.title}"

class DrawingVersion(models.Model):
    """Version control for drawing documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drawing = models.ForeignKey(DrawingDocument, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=10)
    
    # Version Details
    changes_made = models.TextField()
    uploaded_by = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='drawing_versions')
    file = models.FileField(upload_to='drawing_versions/%Y/%m/')
    
    # Approval Workflow
    requires_approval = models.BooleanField(default=True)
    approved_by = models.ForeignKey(RejlersUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_versions')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'drawing_version'
        verbose_name = 'Drawing Version'
        verbose_name_plural = 'Drawing Versions'
        unique_together = ['drawing', 'version_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.drawing.drawing_number} v{self.version_number}"
