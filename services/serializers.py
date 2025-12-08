from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ServiceCategory, Service, ServiceFeature, ServiceBenefit, 
    ServiceProcess, ServiceIndustry, ServiceIndustryMapping,
    ServiceTestimonial, ServiceInquiry
)

User = get_user_model()

class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories"""
    services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color_code',
            'is_active', 'order', 'services_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_services_count(self, obj):
        """Get count of published services in this category"""
        return obj.services.filter(is_published=True).count()

class ServiceIndustrySerializer(serializers.ModelSerializer):
    """Serializer for service industries"""
    
    class Meta:
        model = ServiceIndustry
        fields = [
            'id', 'name', 'description', 'icon', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceIndustryMappingSerializer(serializers.ModelSerializer):
    """Serializer for service industry mapping"""
    industry = ServiceIndustrySerializer(read_only=True)
    industry_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ServiceIndustryMapping
        fields = [
            'id', 'industry', 'industry_id', 'relevance_score', 'notes', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']

class ServiceFeatureSerializer(serializers.ModelSerializer):
    """Serializer for service features"""
    
    class Meta:
        model = ServiceFeature
        fields = [
            'id', 'title', 'description', 'icon', 'is_key_feature', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceBenefitSerializer(serializers.ModelSerializer):
    """Serializer for service benefits"""
    
    class Meta:
        model = ServiceBenefit
        fields = [
            'id', 'title', 'description', 'icon', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceProcessSerializer(serializers.ModelSerializer):
    """Serializer for service process steps"""
    
    class Meta:
        model = ServiceProcess
        fields = [
            'id', 'step_number', 'title', 'description', 'duration', 
            'deliverable', 'icon', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceTestimonialSerializer(serializers.ModelSerializer):
    """Serializer for service testimonials"""
    
    class Meta:
        model = ServiceTestimonial
        fields = [
            'id', 'client_name', 'client_title', 'client_company', 'client_photo',
            'testimonial', 'rating', 'project_name', 'project_duration', 
            'project_value', 'is_featured', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for service relations"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer for service list view (minimal data)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color_code', read_only=True)
    key_features = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    testimonials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name', 
            'category_color', 'service_type', 'duration_min', 'duration_max',
            'base_price', 'price_unit', 'is_price_negotiable', 'featured_image',
            'is_featured', 'is_published', 'popularity_score', 'views_count',
            'key_features', 'average_rating', 'testimonials_count',
            'created_at', 'updated_at'
        ]
    
    def get_key_features(self, obj):
        """Get key features (limit to 3)"""
        features = obj.features.filter(is_key_feature=True)[:3]
        return ServiceFeatureSerializer(features, many=True).data
    
    def get_average_rating(self, obj):
        """Calculate average rating from testimonials"""
        testimonials = obj.testimonials.filter(is_published=True)
        if testimonials:
            total_rating = sum(t.rating for t in testimonials)
            return round(total_rating / len(testimonials), 1)
        return 0
    
    def get_testimonials_count(self, obj):
        """Get count of published testimonials"""
        return obj.testimonials.filter(is_published=True).count()

class ServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for service detail view (complete data)"""
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    created_by = UserSimpleSerializer(read_only=True)
    
    # Related objects
    features = ServiceFeatureSerializer(many=True, read_only=True)
    benefits = ServiceBenefitSerializer(many=True, read_only=True)
    process_steps = ServiceProcessSerializer(many=True, read_only=True)
    industry_mappings = ServiceIndustryMappingSerializer(many=True, read_only=True)
    testimonials = ServiceTestimonialSerializer(many=True, read_only=True)
    
    # Statistics
    average_rating = serializers.SerializerMethodField()
    total_testimonials = serializers.SerializerMethodField()
    total_inquiries = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_id', 'service_type', 'duration_min', 'duration_max',
            'base_price', 'price_unit', 'is_price_negotiable', 'requirements',
            'deliverables', 'methodology', 'required_expertise', 'team_size_min',
            'team_size_max', 'featured_image', 'banner_image', 'brochure_url',
            'is_featured', 'is_published', 'meta_description', 'tags',
            'popularity_score', 'views_count', 'created_at', 'updated_at',
            'created_by', 'features', 'benefits', 'process_steps', 
            'industry_mappings', 'testimonials', 'average_rating', 
            'total_testimonials', 'total_inquiries'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at', 'updated_at', 'created_by']
    
    def get_average_rating(self, obj):
        """Calculate average rating from testimonials"""
        testimonials = obj.testimonials.filter(is_published=True)
        if testimonials:
            total_rating = sum(t.rating for t in testimonials)
            return round(total_rating / len(testimonials), 1)
        return 0
    
    def get_total_testimonials(self, obj):
        """Get total number of published testimonials"""
        return obj.testimonials.filter(is_published=True).count()
    
    def get_total_inquiries(self, obj):
        """Get total number of inquiries"""
        return obj.inquiries.count()
    
    def create(self, validated_data):
        """Create service with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating services"""
    
    class Meta:
        model = Service
        fields = [
            'title', 'description', 'short_description', 'category_id', 'service_type',
            'duration_min', 'duration_max', 'base_price', 'price_unit', 
            'is_price_negotiable', 'requirements', 'deliverables', 'methodology',
            'required_expertise', 'team_size_min', 'team_size_max', 'featured_image',
            'banner_image', 'brochure_url', 'is_featured', 'is_published',
            'meta_description', 'tags', 'popularity_score'
        ]
    
    def validate(self, data):
        """Validate service data"""
        duration_min = data.get('duration_min')
        duration_max = data.get('duration_max')
        
        if duration_min and duration_max and duration_min > duration_max:
            raise serializers.ValidationError("Minimum duration cannot be greater than maximum duration.")
        
        team_size_min = data.get('team_size_min')
        team_size_max = data.get('team_size_max')
        
        if team_size_min and team_size_max and team_size_min > team_size_max:
            raise serializers.ValidationError("Minimum team size cannot be greater than maximum team size.")
        
        return data

class ServiceInquirySerializer(serializers.ModelSerializer):
    """Serializer for service inquiries"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceInquiry
        fields = [
            'id', 'service', 'service_title', 'client_name', 'client_email',
            'client_phone', 'client_company', 'client_title', 'subject',
            'message', 'budget_range', 'timeline', 'urgency', 'status',
            'assigned_to', 'assigned_to_name', 'response_notes', 'follow_up_date',
            'created_at', 'updated_at', 'responded_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'responded_at']

class ServiceInquiryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating service inquiries (public form)"""
    
    class Meta:
        model = ServiceInquiry
        fields = [
            'service', 'client_name', 'client_email', 'client_phone',
            'client_company', 'client_title', 'subject', 'message',
            'budget_range', 'timeline', 'urgency'
        ]
    
    def validate_client_email(self, value):
        """Validate email format"""
        from django.core.validators import validate_email
        try:
            validate_email(value)
        except:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

class ServiceStatsSerializer(serializers.Serializer):
    """Serializer for service statistics"""
    total_services = serializers.IntegerField()
    published_services = serializers.IntegerField()
    featured_services = serializers.IntegerField()
    services_by_category = serializers.DictField()
    services_by_type = serializers.DictField()
    total_inquiries = serializers.IntegerField()
    new_inquiries = serializers.IntegerField()
    pending_inquiries = serializers.IntegerField()
    total_testimonials = serializers.IntegerField()
    average_service_rating = serializers.FloatField()
    most_popular_services = serializers.ListField()
    most_viewed_services = serializers.ListField()

class ServiceSearchSerializer(serializers.Serializer):
    """Serializer for service search parameters"""
    search = serializers.CharField(required=False, help_text="Search in title, description, tags")
    category = serializers.UUIDField(required=False, help_text="Filter by category ID")
    service_type = serializers.ChoiceField(choices=Service._meta.get_field('service_type').choices, required=False)
    min_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    duration_min = serializers.IntegerField(required=False)
    duration_max = serializers.IntegerField(required=False)
    industry = serializers.UUIDField(required=False, help_text="Filter by industry ID")
    rating_min = serializers.IntegerField(min_value=1, max_value=5, required=False)
    is_featured = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)
    tags = serializers.CharField(required=False, help_text="Comma-separated tags")
    has_testimonials = serializers.BooleanField(required=False)
    price_negotiable = serializers.BooleanField(required=False)