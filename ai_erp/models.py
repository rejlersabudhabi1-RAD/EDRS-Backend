from django.db import models
from django.contrib.auth.models import User
from authentication.models import RejlersUser
import uuid
from django.utils import timezone
import json

class ERPRole(models.Model):
    """Enhanced Role model for Oil & Gas ERP system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    permissions = models.JSONField(default=list, help_text="List of permissions")
    redirect_url = models.CharField(max_length=200, help_text="Dashboard URL after login")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_erp_role'
        verbose_name = 'ERP Role'
        verbose_name_plural = 'ERP Roles'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def has_permission(self, permission):
        """Check if role has specific permission"""
        if '*' in self.permissions:
            return True
        return permission in self.permissions or any(
            perm.endswith('*') and permission.startswith(perm[:-1]) 
            for perm in self.permissions
        )

class UserERPProfile(models.Model):
    """Extended user profile for Oil & Gas ERP"""
    EXPERIENCE_LEVELS = [
        ('junior', 'Junior (0-2 years)'),
        ('mid', 'Mid-level (3-5 years)'),
        ('senior', 'Senior (6-10 years)'),
        ('expert', 'Expert (10+ years)'),
        ('consultant', 'Consultant/Specialist'),
    ]
    
    ENGINEERING_DOMAINS = [
        ('upstream', 'Upstream Operations'),
        ('midstream', 'Midstream Operations'),
        ('downstream', 'Downstream Operations'),
        ('offshore', 'Offshore Engineering'),
        ('onshore', 'Onshore Engineering'),
        ('process', 'Process Engineering'),
        ('mechanical', 'Mechanical Engineering'),
        ('electrical', 'Electrical Engineering'),
        ('instrumentation', 'Instrumentation & Controls'),
        ('safety', 'Safety Engineering'),
        ('environmental', 'Environmental Engineering'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RejlersUser, on_delete=models.CASCADE, related_name='erp_profile')
    role = models.ForeignKey(ERPRole, on_delete=models.PROTECT, related_name='users')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    primary_domain = models.CharField(max_length=30, choices=ENGINEERING_DOMAINS)
    secondary_domains = models.JSONField(default=list, help_text="Additional engineering domains")
    
    # Professional Details
    license_number = models.CharField(max_length=50, blank=True)
    certifications = models.JSONField(default=list)
    specializations = models.JSONField(default=list)
    
    # Access Control
    ip_whitelist = models.JSONField(default=list, help_text="Allowed IP addresses")
    access_hours = models.JSONField(default=dict, help_text="Allowed access hours by day")
    max_concurrent_sessions = models.PositiveIntegerField(default=3)
    
    # AI Preferences
    ai_assistant_enabled = models.BooleanField(default=True)
    preferred_ai_model = models.CharField(max_length=50, default='gpt-4o-mini')
    ai_analysis_level = models.CharField(max_length=20, choices=[
        ('basic', 'Basic Analysis'),
        ('detailed', 'Detailed Analysis'),
        ('expert', 'Expert Level Analysis'),
    ], default='detailed')
    
    # Activity Tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    total_drawings_analyzed = models.PositiveIntegerField(default=0)
    total_simulations_run = models.PositiveIntegerField(default=0)
    ai_queries_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_erp_user_profile'
        verbose_name = 'User ERP Profile'
        verbose_name_plural = 'User ERP Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"
    
    def can_access_domain(self, domain):
        """Check if user can access specific engineering domain"""
        return (self.primary_domain == domain or 
                domain in self.secondary_domains or
                self.role.has_permission('*'))

class ProjectERPInfo(models.Model):
    """Extended project information for Oil & Gas ERP"""
    PROJECT_TYPES = [
        ('exploration', 'Exploration'),
        ('development', 'Field Development'),
        ('production', 'Production'),
        ('maintenance', 'Maintenance & Inspection'),
        ('decommissioning', 'Decommissioning'),
        ('pipeline', 'Pipeline Project'),
        ('facility', 'Facility Construction'),
        ('refinery', 'Refinery Project'),
        ('offshore', 'Offshore Platform'),
        ('environmental', 'Environmental Project'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name='erp_info')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    engineering_domain = models.CharField(max_length=30, choices=UserERPProfile.ENGINEERING_DOMAINS)
    
    # Oil & Gas Specific Details
    field_location = models.JSONField(default=dict, help_text="Coordinates and location details")
    water_depth = models.FloatField(null=True, blank=True, help_text="Water depth in meters (for offshore)")
    reservoir_type = models.CharField(max_length=50, blank=True)
    fluid_type = models.CharField(max_length=50, blank=True, help_text="Oil, Gas, Condensate, etc.")
    
    # Safety & Risk Assessment
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='medium')
    safety_requirements = models.JSONField(default=list)
    environmental_considerations = models.JSONField(default=list)
    
    # AI Enhancement
    ai_analysis_enabled = models.BooleanField(default=True)
    ai_recommendations = models.JSONField(default=list)
    predictive_maintenance_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_erp_project_info'
        verbose_name = 'Project ERP Information'
        verbose_name_plural = 'Project ERP Information'
    
    def __str__(self):
        return f"{self.project.title} - {self.project_type}"

class UserActivityLog(models.Model):
    """Real-time user activity tracking for AI-powered monitoring"""
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('page_view', 'Page View'),
        ('document_upload', 'Document Upload'),
        ('document_process', 'Document Processing'),
        ('ai_query', 'AI Query'),
        ('system_config', 'System Configuration'),
        ('user_management', 'User Management Action'),
        ('security_event', 'Security Event'),
        ('performance_issue', 'Performance Issue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    page_url = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} at {self.created_at}"

class AIInsightModel(models.Model):
    """AI-powered insights and recommendations for system optimization"""
    INSIGHT_TYPES = [
        ('user_behavior', 'User Behavior Analysis'),
        ('system_performance', 'System Performance Analysis'),
        ('security_analysis', 'Security Analysis'),
        ('resource_optimization', 'Resource Optimization'),
        ('predictive_maintenance', 'Predictive Maintenance'),
        ('anomaly_detection', 'Anomaly Detection'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical Priority'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    insight_type = models.CharField(max_length=25, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    confidence_score = models.FloatField(help_text='AI confidence level (0.0-1.0)')
    generated_by = models.CharField(max_length=100, help_text='AI model that generated this insight')
    target_users = models.ManyToManyField(RejlersUser, blank=True, related_name='ai_insights')
    action_items = models.JSONField(default=list, help_text='Recommended actions')
    metadata = models.JSONField(default=dict)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(RejlersUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_insights')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_insight_model'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['insight_type', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

class UserSessionTracking(models.Model):
    """Real-time user session tracking for live monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='session_tracking')
    session_id = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    current_page = models.CharField(max_length=500, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.PositiveIntegerField(null=True, blank=True, help_text='Session duration in seconds')
    pages_visited = models.JSONField(default=list)
    actions_performed = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'user_session_tracking'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id']),
            models.Index(fields=['-last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Session {self.session_id[:8]}..."
    
    def get_session_duration(self):
        if self.logout_time:
            return (self.logout_time - self.login_time).total_seconds()
        return (timezone.now() - self.login_time).total_seconds()

class SystemMetrics(models.Model):
    """System performance metrics for AI-powered monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_type = models.CharField(max_length=50)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    threshold_min = models.FloatField(null=True, blank=True)
    threshold_max = models.FloatField(null=True, blank=True)
    is_critical = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_type', '-recorded_at']),
            models.Index(fields=['is_critical']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value}{self.unit}"

class AISystemLog(models.Model):
    """Enhanced AI system activities and decisions with user management integration"""
    LOG_TYPES = [
        ('drawing_analysis', 'Drawing Analysis'),
        ('simulation', 'Simulation'),
        ('recommendation', 'AI Recommendation'),
        ('prediction', 'Predictive Analysis'),
        ('anomaly', 'Anomaly Detection'),
        ('optimization', 'Process Optimization'),
        ('safety_check', 'Safety Analysis'),
        ('cost_estimation', 'Cost Estimation'),
        ('user_behavior_analysis', 'User Behavior Analysis'),
        ('system_optimization', 'System Optimization'),
        ('security_analysis', 'Security Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='ai_logs')
    log_type = models.CharField(max_length=30, choices=LOG_TYPES)
    
    # AI Model Information
    ai_model_used = models.CharField(max_length=100)
    tokens_used = models.PositiveIntegerField(default=0)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    
    # Request/Response Data
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Context
    project_id = models.UUIDField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Results
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_erp_system_log'
        verbose_name = 'AI System Log'
        verbose_name_plural = 'AI System Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.log_type} - {self.user.username} - {self.created_at}"


class FeaturePermission(models.Model):
    """Granular feature permissions for the ERP system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature_name = models.CharField(max_length=100, unique=True)
    feature_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('drawing_analysis', 'Drawing Analysis'),
        ('document_management', 'Document Management'),
        ('project_management', 'Project Management'),
        ('simulation', 'Simulation'),
        ('ai_processing', 'AI Processing'),
        ('user_management', 'User Management'),
        ('system_admin', 'System Administration'),
        ('reporting', 'Reporting & Analytics'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feature_permission'
        verbose_name = 'Feature Permission'
        verbose_name_plural = 'Feature Permissions'

    def __str__(self):
        return f"{self.feature_name} ({self.feature_code})"


class UserFeatureAccess(models.Model):
    """User's access to specific features"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='feature_access')
    feature = models.ForeignKey(FeaturePermission, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(RejlersUser, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    access_level = models.CharField(max_length=20, choices=[
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('admin', 'Full Admin'),
    ], default='read')

    class Meta:
        db_table = 'user_feature_access'
        unique_together = ['user', 'feature']
        verbose_name = 'User Feature Access'
        verbose_name_plural = 'User Feature Access'

    def __str__(self):
        return f"{self.user.username} - {self.feature.feature_name} ({self.access_level})"


class UserS3Storage(models.Model):
    """AWS S3 storage management for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RejlersUser, on_delete=models.CASCADE, related_name='s3_storage')
    s3_bucket_name = models.CharField(max_length=100)
    s3_folder_path = models.CharField(max_length=200)
    storage_quota_gb = models.FloatField(default=10.0)
    current_usage_gb = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_s3_storage'
        verbose_name = 'User S3 Storage'
        verbose_name_plural = 'User S3 Storage'

    def __str__(self):
        return f"{self.user.username} - {self.s3_folder_path}"

    @property
    def storage_usage_percentage(self):
        return (self.current_usage_gb / self.storage_quota_gb) * 100 if self.storage_quota_gb > 0 else 0


class UserLoginHistory(models.Model):
    """Enhanced login history with feature access tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='enhanced_login_history')
    login_timestamp = models.DateTimeField(auto_now_add=True)
    logout_timestamp = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    features_accessed = models.JSONField(default=list)
    session_duration_minutes = models.IntegerField(null=True, blank=True)
    is_successful = models.BooleanField(default=True)
    failure_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'user_login_history'
        verbose_name = 'User Login History'
        verbose_name_plural = 'User Login History'
        ordering = ['-login_timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.login_timestamp}"


class ConsultationRequest(models.Model):
    """Model for storing consultation form submissions"""
    
    PROJECT_TYPE_CHOICES = [
        ('energy-transition', 'Energy Transition'),
        ('industry-transformation', 'Industry Transformation'),
        ('future-proof-communities', 'Future-Proof Communities'),
        ('engineering-consulting', 'Engineering Consulting'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Contact information
    name = models.CharField(max_length=100, verbose_name='Full Name')
    email = models.EmailField(verbose_name='Email Address')
    phone = models.CharField(max_length=20, verbose_name='Phone Number')
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name='Company Name')
    
    # Request details
    subject = models.CharField(max_length=200, verbose_name='Subject')
    project_type = models.CharField(
        max_length=50, 
        choices=PROJECT_TYPE_CHOICES, 
        verbose_name='Project Type'
    )
    message = models.TextField(verbose_name='Message/Requirements')
    
    # Management fields
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Status'
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name='Priority'
    )
    
    # Tracking fields
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        RejlersUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_consultations'
    )
    
    # Communication tracking
    email_sent = models.BooleanField(default=False)
    auto_reply_sent = models.BooleanField(default=False)
    first_response_at = models.DateTimeField(null=True, blank=True)
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, default='website')
    
    class Meta:
        db_table = 'consultation_requests'
        verbose_name = 'Consultation Request'
        verbose_name_plural = 'Consultation Requests'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.name} ({self.get_project_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number: REJ-YYYYMMDD-XXXXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            import random
            random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            self.reference_number = f"REJ-{date_str}-{random_suffix}"
        super().save(*args, **kwargs)
    
    @property
    def age_in_hours(self):
        """Calculate age of request in hours"""
        from django.utils import timezone
        return (timezone.now() - self.submitted_at).total_seconds() / 3600
    
    @property
    def is_overdue(self):
        """Check if request is overdue (more than 24 hours without response)"""
        return self.age_in_hours > 24 and not self.first_response_at
