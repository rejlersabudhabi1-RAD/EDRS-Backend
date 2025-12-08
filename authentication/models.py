from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class RejlersUser(AbstractUser):
    """
    Extended user model for Rejlers system with additional fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Rejlers specific fields
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    office_location = models.CharField(max_length=100, blank=True, 
                                     choices=[
                                         ('abu_dhabi', 'Abu Dhabi'),
                                         ('sweden', 'Sweden'),
                                         ('finland', 'Finland'),
                                         ('norway', 'Norway'),
                                     ])
    
    # Profile information
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    
    # Permissions
    is_team_lead = models.BooleanField(default=False)
    is_project_manager = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='rejlers_users',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='rejlers_users',
        help_text='Specific permissions for this user.',
    )
    
    class Meta:
        verbose_name = 'Rejlers User'
        verbose_name_plural = 'Rejlers Users'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_office_display_name(self):
        office_names = {
            'abu_dhabi': 'Abu Dhabi, UAE',
            'sweden': 'Stockholm, Sweden',
            'finland': 'Helsinki, Finland', 
            'norway': 'Oslo, Norway'
        }
        return office_names.get(self.office_location, 'Unknown Office')


class UserProfile(models.Model):
    """
    Extended profile information for Rejlers users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RejlersUser, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    avatar = models.URLField(blank=True, help_text="Profile picture URL")
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional Information
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    
    # Professional details
    expertise_areas = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    
    # Verification Status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Privacy Settings
    is_public_profile = models.BooleanField(default=True)
    newsletter_subscription = models.BooleanField(default=False)
    
    # Settings
    notification_preferences = models.JSONField(default=dict, blank=True)
    theme_preference = models.CharField(max_length=20, default='light',
                                      choices=[('light', 'Light'), ('dark', 'Dark')])
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"


class LoginHistory(models.Model):
    """
    Track user login history for security purposes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RejlersUser, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_successful = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=200, blank=True)
    
    # Location information
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Device information
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"
