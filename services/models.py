from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class ServiceCategory(models.Model):
    """Service categories for organizing services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class ServiceType(models.TextChoices):
    """Service type choices"""
    CONSULTING = 'consulting', 'Consulting'
    ENGINEERING = 'engineering', 'Engineering'
    DESIGN = 'design', 'Design'
    IMPLEMENTATION = 'implementation', 'Implementation'
    MAINTENANCE = 'maintenance', 'Maintenance'
    TRAINING = 'training', 'Training'
    AUDIT = 'audit', 'Audit'
    RESEARCH = 'research', 'Research'

class Service(models.Model):
    """Main service model for Rejlers services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Service classification
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.CONSULTING)
    
    # Service details
    duration_min = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum duration in days")
    duration_max = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum duration in days")
    
    # Pricing (optional, can be customized per client)
    base_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=50, blank=True, help_text="e.g., per day, per project, per hour")
    is_price_negotiable = models.BooleanField(default=True)
    
    # Requirements and qualifications
    requirements = models.TextField(blank=True, help_text="Client requirements")
    deliverables = models.TextField(blank=True, help_text="Service deliverables")
    methodology = models.TextField(blank=True, help_text="Service methodology")
    
    # Team and expertise
    required_expertise = models.CharField(max_length=200, blank=True)
    team_size_min = models.PositiveIntegerField(null=True, blank=True)
    team_size_max = models.PositiveIntegerField(null=True, blank=True)
    
    # Media
    featured_image = models.URLField(blank=True)
    banner_image = models.URLField(blank=True)
    brochure_url = models.URLField(blank=True)
    
    # SEO and visibility
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    meta_description = models.CharField(max_length=160, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Statistics
    popularity_score = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_services')

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['-popularity_score', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['service_type', 'is_featured']),
            models.Index(fields=['popularity_score', 'views_count']),
        ]

    def __str__(self):
        return self.title

    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

class ServiceFeature(models.Model):
    """Service features and benefits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    is_key_feature = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Feature"
        verbose_name_plural = "Service Features"
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.service.title} - {self.title}"

class ServiceBenefit(models.Model):
    """Service benefits for clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='benefits')
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Benefit"
        verbose_name_plural = "Service Benefits"
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.service.title} - {self.title}"

class ServiceProcess(models.Model):
    """Service process steps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='process_steps')
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 2-3 days, 1 week")
    deliverable = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Process"
        verbose_name_plural = "Service Processes"
        ordering = ['step_number']
        unique_together = ['service', 'step_number']

    def __str__(self):
        return f"{self.service.title} - Step {self.step_number}: {self.title}"

class ServiceIndustry(models.Model):
    """Industries served by services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Industry"
        verbose_name_plural = "Service Industries"
        ordering = ['name']

    def __str__(self):
        return self.name

class ServiceIndustryMapping(models.Model):
    """Many-to-many relationship between services and industries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='industry_mappings')
    industry = models.ForeignKey(ServiceIndustry, on_delete=models.CASCADE, related_name='service_mappings')
    relevance_score = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Relevance score from 1-10"
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Industry Mapping"
        verbose_name_plural = "Service Industry Mappings"
        unique_together = ['service', 'industry']
        ordering = ['-relevance_score']

    def __str__(self):
        return f"{self.service.title} for {self.industry.name}"

class ServiceTestimonial(models.Model):
    """Client testimonials for services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='testimonials')
    client_name = models.CharField(max_length=200)
    client_title = models.CharField(max_length=200, blank=True)
    client_company = models.CharField(max_length=200, blank=True)
    client_photo = models.URLField(blank=True)
    
    # Testimonial content
    testimonial = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 stars"
    )
    
    # Project details (optional)
    project_name = models.CharField(max_length=200, blank=True)
    project_duration = models.CharField(max_length=100, blank=True)
    project_value = models.CharField(max_length=100, blank=True)
    
    # Visibility
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Testimonial"
        verbose_name_plural = "Service Testimonials"
        ordering = ['-rating', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.service.title}"

class ServiceInquiry(models.Model):
    """Service inquiries from potential clients"""
    INQUIRY_STATUS = [
        ('new', 'New'),
        ('reviewing', 'Under Review'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiating', 'Negotiating'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    URGENCY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='inquiries')
    
    # Client information
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True)
    client_company = models.CharField(max_length=200, blank=True)
    client_title = models.CharField(max_length=200, blank=True)
    
    # Inquiry details
    subject = models.CharField(max_length=200)
    message = models.TextField()
    budget_range = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='medium')
    
    # Status and assignment
    status = models.CharField(max_length=20, choices=INQUIRY_STATUS, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_inquiries')
    
    # Response tracking
    response_notes = models.TextField(blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Service Inquiry"
        verbose_name_plural = "Service Inquiries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'urgency']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.client_name} - {self.service.title}"
