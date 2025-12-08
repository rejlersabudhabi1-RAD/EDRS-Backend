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
    Department, Position, SkillCategory, Skill, TeamMember, TeamMemberSkill,
    Education, Certification, TeamProject, TeamMemberProject, Achievement
)
from .serializers import (
    DepartmentSerializer, PositionSerializer, SkillCategorySerializer, SkillSerializer,
    TeamMemberListSerializer, TeamMemberDetailSerializer, TeamMemberCreateUpdateSerializer,
    TeamMemberSkillSerializer, EducationSerializer, CertificationSerializer,
    TeamProjectSerializer, TeamMemberProjectSerializer, AchievementSerializer,
    TeamStatsSerializer, TeamSearchSerializer
)
from authentication.permissions import IsOwnerOrReadOnly

User = get_user_model()

class CustomTeamPagination(PageNumberPagination):
    """Custom pagination for team"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

# Department Views
class DepartmentListView(generics.ListCreateAPIView):
    """List all departments or create a new department"""
    queryset = Department.objects.filter(is_active=True).select_related('head_of_department')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a department"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

# Position Views
class PositionListView(generics.ListCreateAPIView):
    """List all positions or create a new position"""
    queryset = Position.objects.filter(is_active=True).select_related('department')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'level', 'created_at']
    ordering = ['level', 'title']
    filterset_fields = ['department', 'level', 'is_management']

class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a position"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

# Skill Category Views
class SkillCategoryListView(generics.ListCreateAPIView):
    """List all skill categories or create a new category"""
    queryset = SkillCategory.objects.filter(is_active=True)
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']

class SkillCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a skill category"""
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Skill Views
class SkillListView(generics.ListCreateAPIView):
    """List all skills or create a new skill"""
    queryset = Skill.objects.filter(is_active=True).select_related('category')
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category__name', 'created_at']
    ordering = ['category__name', 'name']
    filterset_fields = ['category', 'is_technical']

class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a skill"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Team Member Views
class TeamMemberListView(generics.ListCreateAPIView):
    """List all team members or create a new member"""
    serializer_class = TeamMemberListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomTeamPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio', 'tagline']
    ordering_fields = ['user__first_name', 'user__last_name', 'hire_date', 'years_of_experience', 'created_at']
    ordering = ['-is_featured', 'user__first_name', 'user__last_name']
    filterset_fields = ['department', 'position', 'employment_status', 'experience_level', 'is_featured', 'is_available_for_projects', 'is_remote']

    def get_queryset(self):
        """Get team members queryset with filters"""
        queryset = TeamMember.objects.select_related(
            'user', 'department', 'position', 'reports_to__user'
        ).prefetch_related('member_skills__skill')
        
        # Apply custom filters from query parameters
        search_serializer = TeamSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data
            
            # Experience years filter
            if data.get('min_experience_years') is not None:
                queryset = queryset.filter(years_of_experience__gte=data['min_experience_years'])
            if data.get('max_experience_years') is not None:
                queryset = queryset.filter(years_of_experience__lte=data['max_experience_years'])
            
            # Skill filter
            if data.get('skill'):
                queryset = queryset.filter(member_skills__skill_id=data['skill']).distinct()
            
            # Location filters
            if data.get('location'):
                queryset = queryset.filter(office_location__icontains=data['location'])
            if data.get('country'):
                queryset = queryset.filter(country__icontains=data['country'])
            
            # Rating filter
            if data.get('min_rating'):
                queryset = queryset.filter(client_rating__gte=data['min_rating'])
            
            # Certifications filter
            if data.get('has_certifications'):
                queryset = queryset.filter(certifications__is_active=True).distinct()
            
            # Reports to filter
            if data.get('reports_to'):
                queryset = queryset.filter(reports_to_id=data['reports_to'])
        
        # Show only public profiles for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public_profile=True, employment_status__in=['full_time', 'part_time'])
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == 'POST':
            return TeamMemberCreateUpdateSerializer
        return TeamMemberListSerializer

    def perform_create(self, serializer):
        """Create team member with user association"""
        # This assumes the user_id is provided in the request data
        serializer.save()

class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a team member"""
    queryset = TeamMember.objects.select_related(
        'user', 'department', 'position', 'reports_to__user'
    ).prefetch_related(
        'member_skills__skill__category', 'education', 'certifications',
        'project_assignments__project', 'achievements', 'direct_reports'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method in ['PUT', 'PATCH']:
            return TeamMemberCreateUpdateSerializer
        return TeamMemberDetailSerializer

    def get_object(self):
        """Get team member object, ensuring public profile for non-authenticated users"""
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.is_public_profile:
            from django.http import Http404
            raise Http404()
        return obj

# Featured Team Members View
class FeaturedTeamMembersView(generics.ListAPIView):
    """List featured team members"""
    serializer_class = TeamMemberListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # No pagination for featured members

    def get_queryset(self):
        """Get featured and public team members"""
        return TeamMember.objects.filter(
            is_featured=True, 
            is_public_profile=True,
            employment_status__in=['full_time', 'part_time']
        ).select_related('user', 'department', 'position')[:6]

# Team Member Skills Views
class TeamMemberSkillListCreateView(generics.ListCreateAPIView):
    """List team member skills or add new skill"""
    serializer_class = TeamMemberSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get skills for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.member_skills.select_related('skill__category')

    def perform_create(self, serializer):
        """Create skill with team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        serializer.save(team_member=member)

class TeamMemberSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a team member skill"""
    serializer_class = TeamMemberSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get skills for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.member_skills.select_related('skill__category')

# Education Views
class EducationListCreateView(generics.ListCreateAPIView):
    """List education records or add new education"""
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get education records for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.education.all()

    def perform_create(self, serializer):
        """Create education with team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        serializer.save(team_member=member)

class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an education record"""
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get education records for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.education.all()

# Certification Views
class CertificationListCreateView(generics.ListCreateAPIView):
    """List certifications or add new certification"""
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get certifications for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.certifications.all()

    def perform_create(self, serializer):
        """Create certification with team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        serializer.save(team_member=member)

class CertificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a certification"""
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get certifications for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.certifications.all()

# Team Project Views
class TeamProjectListView(generics.ListCreateAPIView):
    """List all team projects or create new project"""
    queryset = TeamProject.objects.all()
    serializer_class = TeamProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomTeamPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'client_name']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    filterset_fields = ['is_active']

class TeamProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a team project"""
    queryset = TeamProject.objects.all()
    serializer_class = TeamProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Team Member Project Assignment Views
class TeamMemberProjectListCreateView(generics.ListCreateAPIView):
    """List project assignments or add new assignment"""
    serializer_class = TeamMemberProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get project assignments for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.project_assignments.select_related('project')

    def perform_create(self, serializer):
        """Create project assignment with team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        serializer.save(team_member=member)

class TeamMemberProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project assignment"""
    serializer_class = TeamMemberProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get project assignments for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.project_assignments.select_related('project')

# Achievement Views
class AchievementListCreateView(generics.ListCreateAPIView):
    """List achievements or add new achievement"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get achievements for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.achievements.filter(is_public=True) if not self.request.user.is_staff else member.achievements.all()

    def perform_create(self, serializer):
        """Create achievement with team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        serializer.save(team_member=member)

class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an achievement"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get achievements for specific team member"""
        member_id = self.kwargs.get('member_id')
        member = get_object_or_404(TeamMember, id=member_id)
        return member.achievements.all()

# Statistics and Analytics Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_stats_view(request):
    """Get comprehensive team statistics"""
    team_members = TeamMember.objects.all()
    
    # Basic counts
    total_members = team_members.count()
    active_members = team_members.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()
    departments_count = Department.objects.filter(is_active=True).count()
    positions_count = Position.objects.filter(is_active=True).count()
    
    # Members by department
    members_by_department = {}
    for dept in Department.objects.filter(is_active=True):
        members_by_department[dept.name] = team_members.filter(department=dept, employment_status__in=['full_time', 'part_time', 'contract']).count()
    
    # Members by position
    members_by_position = {}
    for position in Position.objects.filter(is_active=True)[:10]:  # Top 10 positions
        members_by_position[position.title] = team_members.filter(position=position, employment_status__in=['full_time', 'part_time', 'contract']).count()
    
    # Members by experience level
    members_by_experience = {}
    for exp_choice in TeamMember._meta.get_field('experience_level').choices:
        members_by_experience[exp_choice[1]] = team_members.filter(experience_level=exp_choice[0]).count()
    
    # Members by location
    members_by_location = {}
    for location in team_members.exclude(office_location='').values_list('office_location', flat=True).distinct()[:10]:
        members_by_location[location] = team_members.filter(office_location=location).count()
    
    # Other statistics
    average_experience_years = team_members.aggregate(avg=Avg('years_of_experience'))['avg'] or 0
    total_skills = TeamMemberSkill.objects.count()
    total_certifications = Certification.objects.filter(is_active=True).count()
    featured_members_count = team_members.filter(is_featured=True).count()
    remote_members_count = team_members.filter(is_remote=True).count()
    
    stats_data = {
        'total_members': total_members,
        'active_members': active_members,
        'departments_count': departments_count,
        'positions_count': positions_count,
        'members_by_department': members_by_department,
        'members_by_position': members_by_position,
        'members_by_experience': members_by_experience,
        'members_by_location': members_by_location,
        'average_experience_years': round(average_experience_years, 1),
        'total_skills': total_skills,
        'total_certifications': total_certifications,
        'featured_members_count': featured_members_count,
        'remote_members_count': remote_members_count
    }
    
    serializer = TeamStatsSerializer(stats_data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_team_stats_view(request):
    """Get public team statistics"""
    team_members = TeamMember.objects.filter(
        is_public_profile=True,
        employment_status__in=['full_time', 'part_time']
    )
    
    stats = {
        'total_team_members': team_members.count(),
        'departments': Department.objects.filter(is_active=True).count(),
        'featured_members': team_members.filter(is_featured=True).count(),
        'remote_members': team_members.filter(is_remote=True).count(),
        'average_experience': round(
            team_members.aggregate(avg=Avg('years_of_experience'))['avg'] or 0, 1
        ),
        'total_skills': Skill.objects.filter(is_active=True).count(),
        'total_certifications': Certification.objects.filter(
            is_active=True,
            team_member__in=team_members
        ).count()
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def team_search_options_view(request):
    """Get available options for team search filters"""
    departments = DepartmentSerializer(
        Department.objects.filter(is_active=True), 
        many=True
    ).data
    
    positions = PositionSerializer(
        Position.objects.filter(is_active=True),
        many=True
    ).data
    
    skills = SkillSerializer(
        Skill.objects.filter(is_active=True),
        many=True
    ).data
    
    employment_statuses = [{'value': choice[0], 'label': choice[1]} for choice in TeamMember._meta.get_field('employment_status').choices]
    experience_levels = [{'value': choice[0], 'label': choice[1]} for choice in TeamMember._meta.get_field('experience_level').choices]
    
    options = {
        'departments': departments,
        'positions': positions,
        'skills': skills,
        'employment_statuses': employment_statuses,
        'experience_levels': experience_levels,
        'locations': list(TeamMember.objects.exclude(office_location='').values_list('office_location', flat=True).distinct()),
        'countries': list(TeamMember.objects.exclude(country='').values_list('country', flat=True).distinct())
    }
    
    return Response(options)
