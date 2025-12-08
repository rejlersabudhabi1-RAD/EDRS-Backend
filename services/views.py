from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .models import (
    ServiceCategory, Service, ServiceFeature, ServiceBenefit,
    ServiceProcess, ServiceIndustry, ServiceIndustryMapping,
    ServiceTestimonial, ServiceInquiry
)
from .serializers import (
    ServiceCategorySerializer, ServiceListSerializer, ServiceDetailSerializer,
    ServiceCreateUpdateSerializer, ServiceFeatureSerializer, ServiceBenefitSerializer,
    ServiceProcessSerializer, ServiceIndustrySerializer, ServiceIndustryMappingSerializer,
    ServiceTestimonialSerializer, ServiceInquirySerializer, ServiceInquiryCreateSerializer,
    ServiceStatsSerializer, ServiceSearchSerializer
)
from authentication.permissions import IsOwnerOrReadOnly

User = get_user_model()

class CustomServicePagination(PageNumberPagination):
    """Custom pagination for services"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

# Service Category Views
class ServiceCategoryListView(generics.ListCreateAPIView):
    """List all service categories or create a new category"""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']

class ServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service category"""
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

# Service Views
class ServiceListView(generics.ListCreateAPIView):
    """List all services or create a new service"""
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomServicePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'short_description', 'tags', 'required_expertise']
    ordering_fields = ['title', 'service_type', 'base_price', 'popularity_score', 'views_count', 'created_at']
    ordering = ['-popularity_score', '-created_at']
    filterset_fields = ['category', 'service_type', 'is_featured', 'is_published', 'is_price_negotiable']

    def get_queryset(self):
        """Get services queryset with filters"""
        queryset = Service.objects.select_related('category', 'created_by').prefetch_related(
            'features', 'testimonials', 'industry_mappings__industry'
        )
        
        # Apply custom filters from query parameters
        search_serializer = ServiceSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data
            
            # Price range filters
            if data.get('min_price'):
                queryset = queryset.filter(base_price__gte=data['min_price'])
            if data.get('max_price'):
                queryset = queryset.filter(base_price__lte=data['max_price'])
            
            # Duration filters
            if data.get('duration_min'):
                queryset = queryset.filter(duration_min__gte=data['duration_min'])
            if data.get('duration_max'):
                queryset = queryset.filter(duration_max__lte=data['duration_max'])
            
            # Industry filter
            if data.get('industry'):
                queryset = queryset.filter(industry_mappings__industry_id=data['industry'])
            
            # Rating filter (services with minimum average rating)
            if data.get('rating_min'):
                # This would require a more complex query with aggregation
                # For now, we'll filter services that have testimonials with high ratings
                queryset = queryset.filter(testimonials__rating__gte=data['rating_min']).distinct()
            
            # Tags filter
            if data.get('tags'):
                tag_list = [tag.strip() for tag in data['tags'].split(',')]
                for tag in tag_list:
                    queryset = queryset.filter(tags__icontains=tag)
            
            # Has testimonials filter
            if data.get('has_testimonials'):
                queryset = queryset.filter(testimonials__is_published=True).distinct()
        
        # Show only published services for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == 'POST':
            return ServiceCreateUpdateSerializer
        return ServiceListSerializer

    def perform_create(self, serializer):
        """Create service with current user as creator"""
        serializer.save(created_by=self.request.user)

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service"""
    queryset = Service.objects.select_related('category', 'created_by').prefetch_related(
        'features', 'benefits', 'process_steps', 'industry_mappings__industry',
        'testimonials', 'inquiries'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method in ['PUT', 'PATCH']:
            return ServiceCreateUpdateSerializer
        return ServiceDetailSerializer

    def get_object(self):
        """Get service object and increment view count"""
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.is_published:
            from django.http import Http404
            raise Http404()
        
        # Increment view count for GET requests
        if self.request.method == 'GET':
            obj.increment_views()
        
        return obj

# Featured Services View
class FeaturedServicesView(generics.ListAPIView):
    """List featured services"""
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # No pagination for featured services

    def get_queryset(self):
        """Get featured and published services"""
        return Service.objects.filter(
            is_featured=True, 
            is_published=True
        ).select_related('category', 'created_by').prefetch_related('features')[:6]

# Service Features Views
class ServiceFeatureListCreateView(generics.ListCreateAPIView):
    """List service features or add new feature"""
    serializer_class = ServiceFeatureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get features for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.features.all()

    def perform_create(self, serializer):
        """Create feature with service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        serializer.save(service=service)

class ServiceFeatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service feature"""
    serializer_class = ServiceFeatureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get features for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.features.all()

# Service Benefits Views
class ServiceBenefitListCreateView(generics.ListCreateAPIView):
    """List service benefits or add new benefit"""
    serializer_class = ServiceBenefitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get benefits for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.benefits.all()

    def perform_create(self, serializer):
        """Create benefit with service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        serializer.save(service=service)

class ServiceBenefitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service benefit"""
    serializer_class = ServiceBenefitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get benefits for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.benefits.all()

# Service Process Views
class ServiceProcessListCreateView(generics.ListCreateAPIView):
    """List service process steps or add new step"""
    serializer_class = ServiceProcessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get process steps for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.process_steps.all()

    def perform_create(self, serializer):
        """Create process step with service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        serializer.save(service=service)

class ServiceProcessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service process step"""
    serializer_class = ServiceProcessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get process steps for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.process_steps.all()

# Service Industries Views
class ServiceIndustryListView(generics.ListCreateAPIView):
    """List all industries or create new industry"""
    queryset = ServiceIndustry.objects.filter(is_active=True)
    serializer_class = ServiceIndustrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class ServiceIndustryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an industry"""
    queryset = ServiceIndustry.objects.all()
    serializer_class = ServiceIndustrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ServiceIndustryMappingView(generics.ListCreateAPIView):
    """List or create industry mappings for a service"""
    serializer_class = ServiceIndustryMappingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get industry mappings for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.industry_mappings.select_related('industry')

    def perform_create(self, serializer):
        """Create industry mapping with service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        serializer.save(service=service)

# Service Testimonials Views
class ServiceTestimonialListCreateView(generics.ListCreateAPIView):
    """List service testimonials or add new testimonial"""
    serializer_class = ServiceTestimonialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get testimonials for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.testimonials.filter(is_published=True)

    def perform_create(self, serializer):
        """Create testimonial with service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        serializer.save(service=service)

class ServiceTestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service testimonial"""
    serializer_class = ServiceTestimonialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get testimonials for specific service"""
        service_slug = self.kwargs.get('service_slug')
        service = get_object_or_404(Service, slug=service_slug)
        return service.testimonials.all()

# Service Inquiries Views
class ServiceInquiryListView(generics.ListAPIView):
    """List service inquiries (admin only)"""
    serializer_class = ServiceInquirySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomServicePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['client_name', 'client_email', 'client_company', 'subject', 'message']
    ordering_fields = ['status', 'urgency', 'created_at', 'updated_at']
    ordering = ['-created_at']
    filterset_fields = ['status', 'urgency', 'assigned_to', 'service']

    def get_queryset(self):
        """Get inquiries based on user permissions"""
        if self.request.user.is_staff:
            return ServiceInquiry.objects.select_related('service', 'assigned_to')
        else:
            # Regular users can only see inquiries assigned to them
            return ServiceInquiry.objects.filter(assigned_to=self.request.user).select_related('service', 'assigned_to')

class ServiceInquiryCreateView(generics.CreateAPIView):
    """Create service inquiry (public)"""
    serializer_class = ServiceInquiryCreateSerializer
    permission_classes = [permissions.AllowAny]

class ServiceInquiryDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update service inquiry (admin only)"""
    serializer_class = ServiceInquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get inquiries based on user permissions"""
        if self.request.user.is_staff:
            return ServiceInquiry.objects.select_related('service', 'assigned_to')
        else:
            return ServiceInquiry.objects.filter(assigned_to=self.request.user).select_related('service', 'assigned_to')

# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def service_stats_view(request):
    """Get comprehensive service statistics"""
    services = Service.objects.all()
    
    # Basic counts
    total_services = services.count()
    published_services = services.filter(is_published=True).count()
    featured_services = services.filter(is_featured=True).count()
    
    # Services by category
    services_by_category = {}
    for category in ServiceCategory.objects.all():
        services_by_category[category.name] = services.filter(category=category).count()
    
    # Services by type
    services_by_type = {}
    from .models import ServiceType
    for service_type in ServiceType.choices:
        services_by_type[service_type[0]] = services.filter(service_type=service_type[0]).count()
    
    # Inquiry statistics
    inquiries = ServiceInquiry.objects.all()
    total_inquiries = inquiries.count()
    new_inquiries = inquiries.filter(status='new').count()
    pending_inquiries = inquiries.filter(status__in=['new', 'reviewing', 'negotiating']).count()
    
    # Testimonial statistics
    testimonials = ServiceTestimonial.objects.filter(is_published=True)
    total_testimonials = testimonials.count()
    average_service_rating = testimonials.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Most popular services
    most_popular_services = list(
        services.filter(is_published=True).order_by('-popularity_score')[:5].values('title', 'popularity_score')
    )
    
    # Most viewed services
    most_viewed_services = list(
        services.filter(is_published=True).order_by('-views_count')[:5].values('title', 'views_count')
    )
    
    stats_data = {
        'total_services': total_services,
        'published_services': published_services,
        'featured_services': featured_services,
        'services_by_category': services_by_category,
        'services_by_type': services_by_type,
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'pending_inquiries': pending_inquiries,
        'total_testimonials': total_testimonials,
        'average_service_rating': round(average_service_rating, 2),
        'most_popular_services': most_popular_services,
        'most_viewed_services': most_viewed_services
    }
    
    serializer = ServiceStatsSerializer(stats_data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_service_stats_view(request):
    """Get public service statistics"""
    services = Service.objects.filter(is_published=True)
    
    stats = {
        'total_services': services.count(),
        'featured_services': services.filter(is_featured=True).count(),
        'service_categories': ServiceCategory.objects.filter(is_active=True).count(),
        'service_industries': ServiceIndustry.objects.filter(is_active=True).count(),
        'total_testimonials': ServiceTestimonial.objects.filter(is_published=True).count(),
        'average_rating': round(
            ServiceTestimonial.objects.filter(is_published=True).aggregate(avg=Avg('rating'))['avg'] or 0, 
            1
        )
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def service_search_options_view(request):
    """Get available options for service search filters"""
    categories = ServiceCategorySerializer(
        ServiceCategory.objects.filter(is_active=True), 
        many=True
    ).data
    
    industries = ServiceIndustrySerializer(
        ServiceIndustry.objects.filter(is_active=True),
        many=True
    ).data
    
    from .models import ServiceType
    service_types = [{'value': choice[0], 'label': choice[1]} for choice in ServiceType.choices]
    
    # Price ranges based on existing services
    price_ranges = [
        {'label': 'Under $1,000', 'min': 0, 'max': 1000},
        {'label': '$1,000 - $5,000', 'min': 1000, 'max': 5000},
        {'label': '$5,000 - $10,000', 'min': 5000, 'max': 10000},
        {'label': '$10,000 - $25,000', 'min': 10000, 'max': 25000},
        {'label': 'Over $25,000', 'min': 25000, 'max': None}
    ]
    
    options = {
        'categories': categories,
        'industries': industries,
        'service_types': service_types,
        'price_ranges': price_ranges,
        'rating_options': [
            {'label': '5 Stars', 'value': 5},
            {'label': '4+ Stars', 'value': 4},
            {'label': '3+ Stars', 'value': 3},
            {'label': '2+ Stars', 'value': 2},
            {'label': '1+ Stars', 'value': 1}
        ]
    }
    
    return Response(options)
