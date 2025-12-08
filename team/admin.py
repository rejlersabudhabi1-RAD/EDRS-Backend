from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department, Position, SkillCategory, Skill, TeamMember, TeamMemberSkill,
    Education, Certification, TeamProject, TeamMemberProject, Achievement
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model"""
    list_display = ['name', 'slug', 'parent_department', 'head_of_department', 'members_count', 'is_active', 'order']
    list_filter = ['is_active', 'parent_department', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'members_count']
    ordering = ['order', 'name']
    
    def members_count(self, obj):
        """Display count of members in this department"""
        return obj.members.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()
    members_count.short_description = 'Active Members'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('parent_department', 'head_of_department')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Admin configuration for Position model"""
    list_display = ['title', 'slug', 'department', 'level', 'is_management', 'members_count', 'is_active']
    list_filter = ['department', 'level', 'is_management', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'created_at', 'members_count']
    ordering = ['department', 'level', 'title']
    
    def members_count(self, obj):
        """Display count of members in this position"""
        return obj.members.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()
    members_count.short_description = 'Active Members'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('department')

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Skill Category model"""
    list_display = ['name', 'color_code_display', 'skills_count', 'is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'skills_count']
    ordering = ['order', 'name']
    
    def color_code_display(self, obj):
        """Display color code with visual representation"""
        if obj.color_code:
            return format_html(
                '<span style="background-color: {}; padding: 3px 10px; color: white;">{}</span>',
                obj.color_code,
                obj.color_code
            )
        return '-'
    color_code_display.short_description = 'Color'
    
    def skills_count(self, obj):
        """Display count of skills in this category"""
        return obj.skills.filter(is_active=True).count()
    skills_count.short_description = 'Skills Count'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin configuration for Skill model"""
    list_display = ['name', 'category', 'is_technical', 'team_members_count', 'is_active']
    list_filter = ['category', 'is_technical', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'team_members_count']
    ordering = ['category', 'name']
    
    def team_members_count(self, obj):
        """Display count of team members with this skill"""
        return obj.team_member_skills.count()
    team_members_count.short_description = 'Team Members'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('category')

class TeamMemberSkillInline(admin.TabularInline):
    """Inline admin for team member skills"""
    model = TeamMemberSkill
    extra = 1
    readonly_fields = ['id', 'added_at']
    fields = ['skill', 'proficiency_level', 'years_of_experience', 'is_certified', 'added_at']

class EducationInline(admin.TabularInline):
    """Inline admin for education"""
    model = Education
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['institution_name', 'degree_type', 'field_of_study', 'start_year', 'end_year', 'is_current', 'created_at']

class CertificationInline(admin.TabularInline):
    """Inline admin for certifications"""
    model = Certification
    extra = 1
    readonly_fields = ['id', 'created_at', 'is_expired']
    fields = ['name', 'issuing_organization', 'issue_date', 'expiration_date', 'is_active', 'is_expired', 'created_at']

class TeamMemberProjectInline(admin.TabularInline):
    """Inline admin for team member projects"""
    model = TeamMemberProject
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['project', 'role', 'start_date', 'end_date', 'is_active', 'created_at']

class AchievementInline(admin.TabularInline):
    """Inline admin for achievements"""
    model = Achievement
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['title', 'achievement_type', 'achievement_date', 'is_featured', 'is_public', 'created_at']

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin configuration for Team Member model"""
    list_display = ['full_name', 'employee_id', 'department', 'position', 'employment_status', 'experience_level', 'hire_date', 'is_featured']
    list_filter = ['department', 'position', 'employment_status', 'experience_level', 'is_featured', 'is_remote', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'bio']
    readonly_fields = ['id', 'full_name', 'is_active_employee', 'created_at', 'updated_at']
    ordering = ['-is_featured', 'user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'profile_image', 'bio', 'tagline')
        }),
        ('Professional Information', {
            'fields': ('department', 'position', 'employment_status', 'experience_level', 'hire_date', 'termination_date')
        }),
        ('Experience', {
            'fields': ('years_of_experience', 'previous_companies')
        }),
        ('Contact Information', {
            'fields': ('work_phone', 'work_email', 'linkedin_profile', 'github_profile', 'portfolio_website')
        }),
        ('Location', {
            'fields': ('office_location', 'country', 'timezone', 'is_remote')
        }),
        ('Reporting', {
            'fields': ('reports_to',)
        }),
        ('Visibility & Status', {
            'fields': ('is_featured', 'is_public_profile', 'is_available_for_projects')
        }),
        ('Statistics', {
            'fields': ('projects_completed', 'client_rating')
        }),
        ('Computed Fields', {
            'fields': ('full_name', 'is_active_employee'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    inlines = [TeamMemberSkillInline, EducationInline, CertificationInline, TeamMemberProjectInline, AchievementInline]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'department', 'position', 'reports_to__user')

@admin.register(TeamMemberSkill)
class TeamMemberSkillAdmin(admin.ModelAdmin):
    """Admin configuration for Team Member Skill model"""
    list_display = ['team_member', 'skill', 'proficiency_level', 'years_of_experience', 'is_certified', 'last_used']
    list_filter = ['proficiency_level', 'is_certified', 'skill__category', 'added_at']
    search_fields = ['team_member__user__first_name', 'team_member__user__last_name', 'skill__name']
    readonly_fields = ['id', 'added_at', 'updated_at']
    ordering = ['team_member', '-proficiency_level', 'skill__name']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('team_member__user', 'skill__category')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin configuration for Education model"""
    list_display = ['team_member', 'institution_name', 'degree_type', 'field_of_study', 'start_year', 'end_year', 'is_current']
    list_filter = ['degree_type', 'is_current', 'start_year', 'end_year']
    search_fields = ['team_member__user__first_name', 'team_member__user__last_name', 'institution_name', 'field_of_study']
    readonly_fields = ['id', 'created_at']
    ordering = ['team_member', '-end_year', '-start_year']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('team_member__user')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin configuration for Certification model"""
    list_display = ['team_member', 'name', 'issuing_organization', 'issue_date', 'expiration_date', 'is_active', 'is_expired']
    list_filter = ['is_active', 'issue_date', 'expiration_date', 'issuing_organization']
    search_fields = ['team_member__user__first_name', 'team_member__user__last_name', 'name', 'issuing_organization']
    readonly_fields = ['id', 'is_expired', 'created_at', 'updated_at']
    ordering = ['team_member', '-issue_date']
    date_hierarchy = 'issue_date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('team_member__user')

@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Team Project model"""
    list_display = ['name', 'client_name', 'start_date', 'end_date', 'is_active', 'team_size', 'project_value']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'client_name']
    readonly_fields = ['id', 'created_at', 'team_size']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    def team_size(self, obj):
        """Display count of team members assigned to this project"""
        return obj.team_assignments.filter(is_active=True).count()
    team_size.short_description = 'Team Size'

@admin.register(TeamMemberProject)
class TeamMemberProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Team Member Project model"""
    list_display = ['team_member', 'project', 'role', 'start_date', 'end_date', 'hours_allocated', 'is_active']
    list_filter = ['role', 'is_active', 'start_date', 'end_date']
    search_fields = ['team_member__user__first_name', 'team_member__user__last_name', 'project__name']
    readonly_fields = ['id', 'created_at']
    ordering = ['team_member', '-start_date']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('team_member__user', 'project')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin configuration for Achievement model"""
    list_display = ['team_member', 'title', 'achievement_type', 'achievement_date', 'is_featured', 'is_public']
    list_filter = ['achievement_type', 'is_featured', 'is_public', 'achievement_date']
    search_fields = ['team_member__user__first_name', 'team_member__user__last_name', 'title', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['team_member', '-achievement_date']
    date_hierarchy = 'achievement_date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('team_member__user')
