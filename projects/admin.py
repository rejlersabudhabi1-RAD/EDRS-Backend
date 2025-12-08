from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProjectCategory, Project, ProjectImage, ProjectMilestone, 
    ProjectTechnology, ProjectTechnologyUsage
)

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Project Category model"""
    list_display = ['name', 'slug', 'projects_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'projects_count']
    ordering = ['name']
    
    def projects_count(self, obj):
        """Display count of projects in this category"""
        return obj.projects.count()
    projects_count.short_description = 'Projects Count'

class ProjectImageInline(admin.TabularInline):
    """Inline admin for project images"""
    model = ProjectImage
    extra = 1
    readonly_fields = ['id', 'uploaded_at']
    fields = ['title', 'image_url', 'alt_text', 'is_cover', 'order', 'uploaded_at']

class ProjectMilestoneInline(admin.TabularInline):
    """Inline admin for project milestones"""
    model = ProjectMilestone
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['title', 'target_date', 'completion_date', 'is_completed', 'completion_percentage', 'order', 'created_at']

class ProjectTechnologyUsageInline(admin.TabularInline):
    """Inline admin for project technology usage"""
    model = ProjectTechnologyUsage
    extra = 1
    readonly_fields = ['id', 'added_at']
    fields = ['technology', 'usage_type', 'notes', 'added_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model"""
    list_display = ['title', 'category', 'status', 'priority', 'progress_percentage', 'start_date', 'end_date', 'is_featured', 'is_published']
    list_filter = ['category', 'status', 'priority', 'is_featured', 'is_published', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'description', 'client_name', 'location', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_overdue', 'duration_days']
    filter_horizontal = []
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category')
        }),
        ('Project Details', {
            'fields': ('status', 'priority', 'start_date', 'end_date', 'estimated_completion', 'progress_percentage')
        }),
        ('Financial Information', {
            'fields': ('budget', 'actual_cost')
        }),
        ('Team & Client', {
            'fields': ('project_manager', 'client_name', 'client_contact', 'client_phone')
        }),
        ('Location', {
            'fields': ('location', 'country', 'coordinates')
        }),
        ('Media', {
            'fields': ('featured_image', 'banner_image')
        }),
        ('SEO & Visibility', {
            'fields': ('is_featured', 'is_published', 'meta_description', 'tags')
        }),
        ('Computed Fields', {
            'fields': ('is_overdue', 'duration_days'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ProjectImageInline, ProjectMilestoneInline, ProjectTechnologyUsageInline]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('category', 'project_manager', 'created_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if not set"""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """Admin configuration for Project Image model"""
    list_display = ['project', 'title', 'is_cover', 'order', 'uploaded_at', 'uploaded_by']
    list_filter = ['is_cover', 'uploaded_at']
    search_fields = ['project__title', 'title', 'alt_text']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['project', 'order', 'uploaded_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('project', 'uploaded_by')

@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    """Admin configuration for Project Milestone model"""
    list_display = ['project', 'title', 'target_date', 'completion_date', 'is_completed', 'completion_percentage', 'order']
    list_filter = ['is_completed', 'target_date', 'completion_date']
    search_fields = ['project__title', 'title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['project', 'order', 'target_date']
    date_hierarchy = 'target_date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('project')

@admin.register(ProjectTechnology)
class ProjectTechnologyAdmin(admin.ModelAdmin):
    """Admin configuration for Project Technology model"""
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'category', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['category', 'name']

@admin.register(ProjectTechnologyUsage)
class ProjectTechnologyUsageAdmin(admin.ModelAdmin):
    """Admin configuration for Project Technology Usage model"""
    list_display = ['project', 'technology', 'usage_type', 'added_at']
    list_filter = ['usage_type', 'added_at', 'technology__category']
    search_fields = ['project__title', 'technology__name', 'usage_type', 'notes']
    readonly_fields = ['id', 'added_at']
    ordering = ['project', 'technology']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('project', 'technology')
