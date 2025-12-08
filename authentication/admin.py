from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import RejlersUser, UserProfile, LoginHistory

@admin.register(RejlersUser)
class RejlersUserAdmin(UserAdmin):
    """Admin configuration for Rejlers User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('id', 'created_at', 'updated_at'),
        }),
    )
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for User Profile model"""
    list_display = ['user', 'phone_number', 'country', 'company', 'email_verified', 'is_public_profile', 'created_at']
    list_filter = ['email_verified', 'is_public_profile', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number', 'company']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio', 'date_of_birth')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Professional Information', {
            'fields': ('company', 'job_title', 'website', 'linkedin_profile')
        }),
        ('Settings', {
            'fields': ('email_verified', 'phone_verified', 'is_public_profile', 'newsletter_subscription')
        }),
        ('Preferences', {
            'fields': ('language', 'timezone', 'notification_preferences')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for Login History model"""
    list_display = ['user', 'ip_address', 'user_agent_display', 'login_time', 'is_successful', 'country']
    list_filter = ['is_successful', 'login_time', 'country', 'device_type']
    search_fields = ['user__username', 'user__email', 'ip_address', 'country', 'city']
    readonly_fields = ['id', 'user', 'ip_address', 'user_agent', 'login_time', 'is_successful', 'failure_reason', 'country', 'city', 'device_type', 'browser', 'os']
    ordering = ['-login_time']
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('Login Information', {
            'fields': ('user', 'login_time', 'is_successful', 'failure_reason')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'device_type', 'browser', 'os')
        }),
        ('Location Information', {
            'fields': ('country', 'city')
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ['collapse']
        })
    )
    
    def user_agent_display(self, obj):
        """Display truncated user agent"""
        if len(obj.user_agent) > 50:
            return obj.user_agent[:50] + '...'
        return obj.user_agent
    user_agent_display.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        """Disable adding login history manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing login history"""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')
