from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Department(models.Model):
    """Departments within Rejlers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_departments')
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Position(models.Model):
    """Job positions/titles within Rejlers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    level = models.PositiveIntegerField(default=1, help_text="Hierarchy level (1=entry, 5=senior)")
    is_management = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        ordering = ['level', 'title']

    def __str__(self):
        return self.title

class SkillCategory(models.Model):
    """Categories for organizing skills"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Skill(models.Model):
    """Skills that team members can have"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    description = models.TextField(blank=True)
    is_technical = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class TeamMember(models.Model):
    """Extended profile for team members"""
    EMPLOYMENT_STATUS = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('consultant', 'Consultant'),
        ('intern', 'Intern'),
        ('inactive', 'Inactive'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('mid', 'Mid Level (4-7 years)'),
        ('senior', 'Senior (7-12 years)'),
        ('lead', 'Lead (12+ years)'),
        ('executive', 'Executive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team_member_profile')
    
    # Basic Information
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    profile_image = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    
    # Professional Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    employment_status = models.CharField(max_length=15, choices=EMPLOYMENT_STATUS, default='full_time')
    experience_level = models.CharField(max_length=15, choices=EXPERIENCE_LEVELS, default='entry')
    
    # Dates
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    
    # Experience
    years_of_experience = models.PositiveIntegerField(default=0)
    previous_companies = models.TextField(blank=True, help_text="Previous work experience")
    
    # Contact Information
    work_phone = models.CharField(max_length=20, blank=True)
    work_email = models.EmailField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    portfolio_website = models.URLField(blank=True)
    
    # Location
    office_location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    is_remote = models.BooleanField(default=False)
    
    # Reporting
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    
    # Visibility and Status
    is_featured = models.BooleanField(default=False)
    is_public_profile = models.BooleanField(default=True)
    is_available_for_projects = models.BooleanField(default=True)
    
    # Statistics
    projects_completed = models.PositiveIntegerField(default=0)
    client_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ['-is_featured', 'user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['department', 'employment_status']),
            models.Index(fields=['is_public_profile', 'is_featured']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position.title if self.position else 'No Position'}"

    @property
    def full_name(self):
        """Get full name from user"""
        return self.user.get_full_name()

    @property
    def is_active_employee(self):
        """Check if employee is currently active"""
        return self.employment_status != 'inactive' and not self.termination_date

class TeamMemberSkill(models.Model):
    """Skills possessed by team members with proficiency levels"""
    PROFICIENCY_LEVELS = [
        (1, 'Beginner'),
        (2, 'Basic'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='member_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='team_member_skills')
    proficiency_level = models.PositiveIntegerField(
        choices=PROFICIENCY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    is_certified = models.BooleanField(default=False)
    certification_details = models.TextField(blank=True)
    last_used = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Team Member Skill"
        verbose_name_plural = "Team Member Skills"
        unique_together = ['team_member', 'skill']
        ordering = ['-proficiency_level', 'skill__name']

    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.skill.name} (Level {self.proficiency_level})"

class Education(models.Model):
    """Education records for team members"""
    DEGREE_TYPES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='education')
    institution_name = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=15, choices=DEGREE_TYPES)
    field_of_study = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    achievements = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
        ordering = ['-end_year', '-start_year']

    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.degree_type} in {self.field_of_study}"

class Certification(models.Model):
    """Professional certifications for team members"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    credential_id = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    verification_url = models.URLField(blank=True)
    certificate_image = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.name}"

    @property
    def is_expired(self):
        """Check if certification is expired"""
        if self.expiration_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiration_date
        return False

class TeamProject(models.Model):
    """Projects that team members work on (separate from main Projects app)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    client_name = models.CharField(max_length=200, blank=True)
    project_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Team Project"
        verbose_name_plural = "Team Projects"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class TeamMemberProject(models.Model):
    """Many-to-many relationship between team members and projects"""
    ROLES = [
        ('project_manager', 'Project Manager'),
        ('team_lead', 'Team Lead'),
        ('senior_engineer', 'Senior Engineer'),
        ('engineer', 'Engineer'),
        ('junior_engineer', 'Junior Engineer'),
        ('consultant', 'Consultant'),
        ('analyst', 'Analyst'),
        ('designer', 'Designer'),
        ('researcher', 'Researcher'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='project_assignments')
    project = models.ForeignKey(TeamProject, on_delete=models.CASCADE, related_name='team_assignments')
    role = models.CharField(max_length=20, choices=ROLES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hours_allocated = models.PositiveIntegerField(null=True, blank=True, help_text="Hours per week")
    responsibilities = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Team Member Project"
        verbose_name_plural = "Team Member Projects"
        unique_together = ['team_member', 'project']
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.project.name} ({self.role})"

class Achievement(models.Model):
    """Achievements and recognitions for team members"""
    ACHIEVEMENT_TYPES = [
        ('award', 'Award'),
        ('recognition', 'Recognition'),
        ('publication', 'Publication'),
        ('patent', 'Patent'),
        ('speaking', 'Speaking Engagement'),
        ('leadership', 'Leadership Role'),
        ('milestone', 'Project Milestone'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    achievement_type = models.CharField(max_length=15, choices=ACHIEVEMENT_TYPES, default='recognition')
    description = models.TextField()
    issuing_organization = models.CharField(max_length=200, blank=True)
    achievement_date = models.DateField()
    verification_url = models.URLField(blank=True)
    image = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ['-achievement_date']

    def __str__(self):
        return f"{self.team_member.user.get_full_name()} - {self.title}"
