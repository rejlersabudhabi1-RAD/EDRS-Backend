from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ProjectCategory, Project, ProjectImage, ProjectMilestone, 
    ProjectTechnology, ProjectTechnologyUsage
)

User = get_user_model()

class ProjectCategorySerializer(serializers.ModelSerializer):
    """Serializer for project categories"""
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'is_active',
            'projects_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_projects_count(self, obj):
        """Get count of published projects in this category"""
        return obj.projects.filter(is_published=True).count()

class ProjectTechnologySerializer(serializers.ModelSerializer):
    """Serializer for project technologies"""
    
    class Meta:
        model = ProjectTechnology
        fields = [
            'id', 'name', 'category', 'description', 'icon', 'website',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ProjectTechnologyUsageSerializer(serializers.ModelSerializer):
    """Serializer for project technology usage"""
    technology = ProjectTechnologySerializer(read_only=True)
    technology_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ProjectTechnologyUsage
        fields = [
            'id', 'technology', 'technology_id', 'usage_type', 'notes', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']

class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer for project images"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectImage
        fields = [
            'id', 'title', 'image_url', 'alt_text', 'description', 'is_cover',
            'order', 'uploaded_at', 'uploaded_by_name'
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_name']

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for project milestones"""
    is_overdue = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'title', 'description', 'target_date', 'completion_date',
            'is_completed', 'completion_percentage', 'order', 'is_overdue',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_overdue(self, obj):
        """Check if milestone is overdue"""
        if not obj.is_completed and obj.target_date:
            from django.utils import timezone
            return timezone.now().date() > obj.target_date
        return False
    
    def get_status(self, obj):
        """Get milestone status"""
        if obj.is_completed:
            return 'completed'
        elif self.get_is_overdue(obj):
            return 'overdue'
        else:
            return 'pending'

class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for project relations"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for project list view (minimal data)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.get_full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    images_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name',
            'status', 'priority', 'start_date', 'end_date', 'progress_percentage',
            'project_manager_name', 'client_name', 'location', 'featured_image',
            'is_featured', 'is_published', 'is_overdue', 'duration_days',
            'images_count', 'created_at', 'updated_at'
        ]
    
    def get_images_count(self, obj):
        """Get count of project images"""
        return obj.images.count()

class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project detail view (complete data)"""
    category = ProjectCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    project_manager = UserSimpleSerializer(read_only=True)
    project_manager_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    created_by = UserSimpleSerializer(read_only=True)
    
    # Related objects
    images = ProjectImageSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    technology_usage = ProjectTechnologyUsageSerializer(many=True, read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    
    # Statistics
    total_milestones = serializers.SerializerMethodField()
    completed_milestones = serializers.SerializerMethodField()
    milestone_completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_id', 'status', 'priority', 'start_date',
            'end_date', 'estimated_completion', 'budget', 'actual_cost',
            'project_manager', 'project_manager_id', 'client_name',
            'client_contact', 'client_phone', 'location', 'country',
            'coordinates', 'featured_image', 'banner_image', 'is_featured',
            'is_published', 'meta_description', 'tags', 'progress_percentage',
            'is_overdue', 'duration_days', 'created_at', 'updated_at',
            'created_by', 'images', 'milestones', 'technology_usage',
            'total_milestones', 'completed_milestones', 'milestone_completion_rate'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'created_by']
    
    def get_total_milestones(self, obj):
        """Get total number of milestones"""
        return obj.milestones.count()
    
    def get_completed_milestones(self, obj):
        """Get number of completed milestones"""
        return obj.milestones.filter(is_completed=True).count()
    
    def get_milestone_completion_rate(self, obj):
        """Get milestone completion percentage"""
        total = self.get_total_milestones(obj)
        if total == 0:
            return 0
        completed = self.get_completed_milestones(obj)
        return round((completed / total) * 100, 2)
    
    def create(self, validated_data):
        """Create project with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating projects"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'short_description', 'category_id',
            'status', 'priority', 'start_date', 'end_date', 'estimated_completion',
            'budget', 'actual_cost', 'project_manager_id', 'client_name',
            'client_contact', 'client_phone', 'location', 'country',
            'coordinates', 'featured_image', 'banner_image', 'is_featured',
            'is_published', 'meta_description', 'tags', 'progress_percentage'
        ]
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage"""
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Progress percentage must be between 0 and 100.")
        return value
    
    def validate(self, data):
        """Validate project data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date.")
        
        budget = data.get('budget')
        actual_cost = data.get('actual_cost', 0)
        
        if budget and actual_cost and actual_cost > budget * 1.5:  # Allow 50% budget overrun
            raise serializers.ValidationError("Actual cost significantly exceeds budget.")
        
        return data

class ProjectStatsSerializer(serializers.Serializer):
    """Serializer for project statistics"""
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    overdue_projects = serializers.IntegerField()
    projects_by_status = serializers.DictField()
    projects_by_priority = serializers.DictField()
    projects_by_category = serializers.DictField()
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_actual_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_progress = serializers.FloatField()
    
class ProjectSearchSerializer(serializers.Serializer):
    """Serializer for project search parameters"""
    search = serializers.CharField(required=False, help_text="Search in title, description, client name")
    category = serializers.UUIDField(required=False, help_text="Filter by category ID")
    status = serializers.ChoiceField(choices=Project._meta.get_field('status').choices, required=False)
    priority = serializers.ChoiceField(choices=Project._meta.get_field('priority').choices, required=False)
    project_manager = serializers.UUIDField(required=False, help_text="Filter by project manager ID")
    is_featured = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)
    start_date_from = serializers.DateField(required=False)
    start_date_to = serializers.DateField(required=False)
    end_date_from = serializers.DateField(required=False)
    end_date_to = serializers.DateField(required=False)
    budget_min = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    budget_max = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    progress_min = serializers.IntegerField(min_value=0, max_value=100, required=False)
    progress_max = serializers.IntegerField(min_value=0, max_value=100, required=False)
    tags = serializers.CharField(required=False, help_text="Comma-separated tags")
    location = serializers.CharField(required=False)
    country = serializers.CharField(required=False)