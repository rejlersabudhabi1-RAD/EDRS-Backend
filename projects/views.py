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
    ProjectCategory, Project, ProjectImage, ProjectMilestone,
    ProjectTechnology, ProjectTechnologyUsage, ProjectStatus, ProjectPriority
)
from .serializers import (
    ProjectCategorySerializer, ProjectListSerializer, ProjectDetailSerializer,
    ProjectCreateUpdateSerializer, ProjectImageSerializer, ProjectMilestoneSerializer,
    ProjectTechnologySerializer, ProjectTechnologyUsageSerializer,
    ProjectStatsSerializer, ProjectSearchSerializer
)
from authentication.permissions import IsOwnerOrReadOnly

User = get_user_model()

class CustomProjectPagination(PageNumberPagination):
    """Custom pagination for projects"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

# Project Category Views
class ProjectCategoryListView(generics.ListCreateAPIView):
    """List all project categories or create a new category"""
    queryset = ProjectCategory.objects.filter(is_active=True)
    serializer_class = ProjectCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class ProjectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project category"""
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

# Project Views
class ProjectListView(generics.ListCreateAPIView):
    """List all projects or create a new project"""
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomProjectPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'short_description', 'client_name', 'location', 'tags']
    ordering_fields = ['title', 'start_date', 'end_date', 'priority', 'status', 'progress_percentage', 'created_at']
    ordering = ['-created_at']
    filterset_fields = ['category', 'status', 'priority', 'is_featured', 'is_published', 'project_manager']

    def get_queryset(self):
        """Get projects queryset with filters"""
        queryset = Project.objects.select_related('category', 'project_manager').prefetch_related('images')
        
        # Apply custom filters from query parameters
        search_serializer = ProjectSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data
            
            # Date range filters
            if data.get('start_date_from'):
                queryset = queryset.filter(start_date__gte=data['start_date_from'])
            if data.get('start_date_to'):
                queryset = queryset.filter(start_date__lte=data['start_date_to'])
            if data.get('end_date_from'):
                queryset = queryset.filter(end_date__gte=data['end_date_from'])
            if data.get('end_date_to'):
                queryset = queryset.filter(end_date__lte=data['end_date_to'])
            
            # Budget filters
            if data.get('budget_min'):
                queryset = queryset.filter(budget__gte=data['budget_min'])
            if data.get('budget_max'):
                queryset = queryset.filter(budget__lte=data['budget_max'])
            
            # Progress filters
            if data.get('progress_min') is not None:
                queryset = queryset.filter(progress_percentage__gte=data['progress_min'])
            if data.get('progress_max') is not None:
                queryset = queryset.filter(progress_percentage__lte=data['progress_max'])
            
            # Tags filter
            if data.get('tags'):
                tag_list = [tag.strip() for tag in data['tags'].split(',')]
                for tag in tag_list:
                    queryset = queryset.filter(tags__icontains=tag)
            
            # Location filters
            if data.get('location'):
                queryset = queryset.filter(location__icontains=data['location'])
            if data.get('country'):
                queryset = queryset.filter(country__icontains=data['country'])
        
        # Show only published projects for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == 'POST':
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer

    def perform_create(self, serializer):
        """Create project with current user as creator"""
        serializer.save(created_by=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project"""
    queryset = Project.objects.select_related('category', 'project_manager', 'created_by').prefetch_related(
        'images', 'milestones', 'technology_usage__technology'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def get_object(self):
        """Get project object, ensuring published for non-authenticated users"""
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.is_published:
            from django.http import Http404
            raise Http404()
        return obj

# Featured Projects View
class FeaturedProjectsView(generics.ListAPIView):
    """List featured projects"""
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # No pagination for featured projects

    def get_queryset(self):
        """Get featured and published projects"""
        return Project.objects.filter(
            is_featured=True, 
            is_published=True
        ).select_related('category', 'project_manager')[:6]  # Limit to 6 featured projects

# Project Images Views
class ProjectImageListCreateView(generics.ListCreateAPIView):
    """List project images or add new image"""
    serializer_class = ProjectImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get images for specific project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.images.all()

    def perform_create(self, serializer):
        """Create image with project and user"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project, uploaded_by=self.request.user)

class ProjectImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project image"""
    serializer_class = ProjectImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Get images for specific project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.images.all()

# Project Milestones Views
class ProjectMilestoneListCreateView(generics.ListCreateAPIView):
    """List project milestones or create new milestone"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get milestones for specific project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.milestones.all()

    def perform_create(self, serializer):
        """Create milestone with project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project)

class ProjectMilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project milestone"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get milestones for specific project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.milestones.all()

# Project Technologies Views
class ProjectTechnologyListView(generics.ListCreateAPIView):
    """List all technologies or create new technology"""
    queryset = ProjectTechnology.objects.filter(is_active=True)
    serializer_class = ProjectTechnologySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'category', 'description']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['name']

class ProjectTechnologyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a technology"""
    queryset = ProjectTechnology.objects.all()
    serializer_class = ProjectTechnologySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProjectTechnologyUsageView(generics.ListCreateAPIView):
    """List or create technology usage for a project"""
    serializer_class = ProjectTechnologyUsageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get technology usage for specific project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.technology_usage.select_related('technology')

    def perform_create(self, serializer):
        """Create technology usage with project"""
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project)

# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_stats_view(request):
    """Get comprehensive project statistics"""
    projects = Project.objects.all()
    
    # Basic counts
    total_projects = projects.count()
    active_projects = projects.filter(status__in=[ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS]).count()
    completed_projects = projects.filter(status=ProjectStatus.COMPLETED).count()
    
    # Overdue projects
    overdue_projects = sum(1 for p in projects if p.is_overdue)
    
    # Projects by status
    projects_by_status = {}
    for status_choice in ProjectStatus.choices:
        projects_by_status[status_choice[0]] = projects.filter(status=status_choice[0]).count()
    
    # Projects by priority
    projects_by_priority = {}
    for priority_choice in ProjectPriority.choices:
        projects_by_priority[priority_choice[0]] = projects.filter(priority=priority_choice[0]).count()
    
    # Projects by category
    projects_by_category = {}
    for category in ProjectCategory.objects.all():
        projects_by_category[category.name] = projects.filter(category=category).count()
    
    # Financial statistics
    total_budget = projects.aggregate(total=Sum('budget'))['total'] or 0
    total_actual_cost = projects.aggregate(total=Sum('actual_cost'))['total'] or 0
    
    # Progress statistics
    average_progress = projects.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
    
    stats_data = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'projects_by_status': projects_by_status,
        'projects_by_priority': projects_by_priority,
        'projects_by_category': projects_by_category,
        'total_budget': total_budget,
        'total_actual_cost': total_actual_cost,
        'average_progress': round(average_progress, 2)
    }
    
    serializer = ProjectStatsSerializer(stats_data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_project_stats_view(request):
    """Get public project statistics (published projects only)"""
    projects = Project.objects.filter(is_published=True)
    
    stats = {
        'total_published_projects': projects.count(),
        'completed_projects': projects.filter(status=ProjectStatus.COMPLETED).count(),
        'active_projects': projects.filter(status__in=[ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS]).count(),
        'featured_projects': projects.filter(is_featured=True).count(),
        'categories': ProjectCategory.objects.filter(is_active=True).count(),
        'technologies': ProjectTechnology.objects.filter(is_active=True).count(),
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def project_search_options_view(request):
    """Get available options for project search filters"""
    categories = ProjectCategorySerializer(
        ProjectCategory.objects.filter(is_active=True), 
        many=True
    ).data
    
    project_managers = []
    for user in User.objects.filter(managed_projects__isnull=False).distinct():
        project_managers.append({
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email
        })
    
    options = {
        'categories': categories,
        'statuses': [{'value': choice[0], 'label': choice[1]} for choice in ProjectStatus.choices],
        'priorities': [{'value': choice[0], 'label': choice[1]} for choice in ProjectPriority.choices],
        'project_managers': project_managers,
        'countries': list(Project.objects.exclude(country='').values_list('country', flat=True).distinct()),
        'locations': list(Project.objects.exclude(location='').values_list('location', flat=True).distinct()[:20])  # Limit to 20 locations
    }
    
    return Response(options)
