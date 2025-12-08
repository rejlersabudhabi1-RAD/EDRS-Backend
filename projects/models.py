from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class ProjectCategory(models.Model):
    """Project categories for organizing projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProjectStatus(models.TextChoices):
    """Project status choices"""
    PLANNING = 'planning', 'Planning'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    ON_HOLD = 'on_hold', 'On Hold'
    CANCELLED = 'cancelled', 'Cancelled'

class ProjectPriority(models.TextChoices):
    """Project priority choices"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'

class Project(models.Model):
    """Main project model for Rejlers projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Project details
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING)
    priority = models.CharField(max_length=10, choices=ProjectPriority.choices, default=ProjectPriority.MEDIUM)
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    
    # Financial
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    
    # Team and client
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    client_name = models.CharField(max_length=200)
    client_contact = models.EmailField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    coordinates = models.CharField(max_length=100, blank=True, help_text="Latitude,Longitude")
    
    # Media
    featured_image = models.URLField(blank=True)
    banner_image = models.URLField(blank=True)
    
    # SEO and visibility
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    meta_description = models.CharField(max_length=160, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.end_date and self.status != ProjectStatus.COMPLETED:
            from django.utils import timezone
            return timezone.now().date() > self.end_date
        return False

    @property
    def duration_days(self):
        """Calculate project duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

class ProjectImage(models.Model):
    """Project gallery images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=200, blank=True)
    image_url = models.URLField()
    alt_text = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.project.title} - {self.title or 'Image'}"

class ProjectMilestone(models.Model):
    """Project milestones and achievements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project Milestone"
        verbose_name_plural = "Project Milestones"
        ordering = ['order', 'target_date']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class ProjectTechnology(models.Model):
    """Technologies used in projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Project Technology"
        verbose_name_plural = "Project Technologies"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProjectTechnologyUsage(models.Model):
    """Many-to-many relationship between projects and technologies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='technology_usage')
    technology = models.ForeignKey(ProjectTechnology, on_delete=models.CASCADE, related_name='project_usage')
    usage_type = models.CharField(max_length=50, blank=True, help_text="e.g., Primary, Secondary, Testing")
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Project Technology Usage"
        verbose_name_plural = "Project Technology Usage"
        unique_together = ['project', 'technology']

    def __str__(self):
        return f"{self.project.title} uses {self.technology.name}"
