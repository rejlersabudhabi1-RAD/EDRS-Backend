from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ServiceCategory, Service, ServiceFeature, ServiceBenefit, 
    ServiceProcess, ServiceIndustry, ServiceIndustryMapping,
    ServiceTestimonial, ServiceInquiry
)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Service Category model"""
    list_display = ['name', 'slug', 'color_code_display', 'services_count', 'is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'services_count']
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
    
    def services_count(self, obj):
        """Display count of services in this category"""
        return obj.services.count()
    services_count.short_description = 'Services Count'

class ServiceFeatureInline(admin.TabularInline):
    """Inline admin for service features"""
    model = ServiceFeature
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['title', 'description', 'icon', 'is_key_feature', 'order', 'created_at']

class ServiceBenefitInline(admin.TabularInline):
    """Inline admin for service benefits"""
    model = ServiceBenefit
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['title', 'description', 'icon', 'order', 'created_at']

class ServiceProcessInline(admin.TabularInline):
    """Inline admin for service process"""
    model = ServiceProcess
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['step_number', 'title', 'description', 'duration', 'deliverable', 'created_at']

class ServiceIndustryMappingInline(admin.TabularInline):
    """Inline admin for service industry mappings"""
    model = ServiceIndustryMapping
    extra = 1
    readonly_fields = ['id', 'added_at']
    fields = ['industry', 'relevance_score', 'notes', 'added_at']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration for Service model"""
    list_display = ['title', 'category', 'service_type', 'base_price', 'popularity_score', 'views_count', 'is_featured', 'is_published']
    list_filter = ['category', 'service_type', 'is_featured', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'tags', 'required_expertise']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'views_count', 'created_at', 'updated_at']
    ordering = ['-popularity_score', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category', 'service_type')
        }),
        ('Duration & Team', {
            'fields': ('duration_min', 'duration_max', 'required_expertise', 'team_size_min', 'team_size_max')
        }),
        ('Pricing', {
            'fields': ('base_price', 'price_unit', 'is_price_negotiable')
        }),
        ('Service Details', {
            'fields': ('requirements', 'deliverables', 'methodology')
        }),
        ('Media', {
            'fields': ('featured_image', 'banner_image', 'brochure_url')
        }),
        ('SEO & Visibility', {
            'fields': ('is_featured', 'is_published', 'meta_description', 'tags', 'popularity_score')
        }),
        ('Statistics', {
            'fields': ('views_count',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ServiceFeatureInline, ServiceBenefitInline, ServiceProcessInline, ServiceIndustryMappingInline]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('category', 'created_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if not set"""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    """Admin configuration for Service Feature model"""
    list_display = ['service', 'title', 'is_key_feature', 'order', 'created_at']
    list_filter = ['is_key_feature', 'created_at']
    search_fields = ['service__title', 'title', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['service', 'order']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service')

@admin.register(ServiceBenefit)
class ServiceBenefitAdmin(admin.ModelAdmin):
    """Admin configuration for Service Benefit model"""
    list_display = ['service', 'title', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['service__title', 'title', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['service', 'order']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service')

@admin.register(ServiceProcess)
class ServiceProcessAdmin(admin.ModelAdmin):
    """Admin configuration for Service Process model"""
    list_display = ['service', 'step_number', 'title', 'duration', 'created_at']
    list_filter = ['created_at']
    search_fields = ['service__title', 'title', 'description', 'deliverable']
    readonly_fields = ['id', 'created_at']
    ordering = ['service', 'step_number']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service')

@admin.register(ServiceIndustry)
class ServiceIndustryAdmin(admin.ModelAdmin):
    """Admin configuration for Service Industry model"""
    list_display = ['name', 'is_active', 'services_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'services_count']
    ordering = ['name']
    
    def services_count(self, obj):
        """Display count of services for this industry"""
        return obj.service_mappings.count()
    services_count.short_description = 'Services Count'

@admin.register(ServiceIndustryMapping)
class ServiceIndustryMappingAdmin(admin.ModelAdmin):
    """Admin configuration for Service Industry Mapping model"""
    list_display = ['service', 'industry', 'relevance_score', 'added_at']
    list_filter = ['relevance_score', 'added_at', 'industry']
    search_fields = ['service__title', 'industry__name', 'notes']
    readonly_fields = ['id', 'added_at']
    ordering = ['service', '-relevance_score']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service', 'industry')

@admin.register(ServiceTestimonial)
class ServiceTestimonialAdmin(admin.ModelAdmin):
    """Admin configuration for Service Testimonial model"""
    list_display = ['service', 'client_name', 'client_company', 'rating', 'is_featured', 'is_published', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_published', 'created_at']
    search_fields = ['service__title', 'client_name', 'client_company', 'testimonial']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-rating', '-created_at']
    
    fieldsets = (
        ('Service & Client', {
            'fields': ('service', 'client_name', 'client_title', 'client_company', 'client_photo')
        }),
        ('Testimonial', {
            'fields': ('testimonial', 'rating')
        }),
        ('Project Details', {
            'fields': ('project_name', 'project_duration', 'project_value')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_published')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service')

@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(admin.ModelAdmin):
    """Admin configuration for Service Inquiry model"""
    list_display = ['service', 'client_name', 'client_company', 'status', 'urgency', 'created_at', 'assigned_to']
    list_filter = ['status', 'urgency', 'assigned_to', 'created_at']
    search_fields = ['service__title', 'client_name', 'client_email', 'client_company', 'subject', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Service & Client', {
            'fields': ('service', 'client_name', 'client_email', 'client_phone', 'client_company', 'client_title')
        }),
        ('Inquiry Details', {
            'fields': ('subject', 'message', 'budget_range', 'timeline', 'urgency')
        }),
        ('Management', {
            'fields': ('status', 'assigned_to', 'response_notes', 'follow_up_date')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'responded_at'),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('service', 'assigned_to')
    
    actions = ['mark_as_reviewed', 'assign_to_me']
    
    def mark_as_reviewed(self, request, queryset):
        """Mark selected inquiries as reviewed"""
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} inquiries marked as under review.')
    mark_as_reviewed.short_description = 'Mark as under review'
    
    def assign_to_me(self, request, queryset):
        """Assign selected inquiries to current user"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{updated} inquiries assigned to you.')
    assign_to_me.short_description = 'Assign to me'
