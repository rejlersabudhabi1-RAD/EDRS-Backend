from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Department, Position, SkillCategory, Skill, TeamMember, TeamMemberSkill,
    Education, Certification, TeamProject, TeamMemberProject, Achievement
)

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for departments"""
    head_name = serializers.CharField(source='head_of_department.get_full_name', read_only=True)
    members_count = serializers.SerializerMethodField()
    sub_departments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color_code',
            'parent_department', 'head_of_department', 'head_name', 'is_active',
            'order', 'members_count', 'sub_departments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        """Get count of active members in this department"""
        return obj.members.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()
    
    def get_sub_departments_count(self, obj):
        """Get count of sub-departments"""
        return obj.sub_departments.filter(is_active=True).count()

class PositionSerializer(serializers.ModelSerializer):
    """Serializer for positions"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'title', 'slug', 'description', 'department', 'department_name',
            'level', 'is_management', 'is_active', 'members_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_members_count(self, obj):
        """Get count of members in this position"""
        return obj.members.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()

class SkillCategorySerializer(serializers.ModelSerializer):
    """Serializer for skill categories"""
    skills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color_code', 'is_active',
            'order', 'skills_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_skills_count(self, obj):
        """Get count of active skills in this category"""
        return obj.skills.filter(is_active=True).count()

class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    team_members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'category_name', 'description',
            'is_technical', 'is_active', 'team_members_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_team_members_count(self, obj):
        """Get count of team members with this skill"""
        return obj.team_member_skills.count()

class TeamMemberSkillSerializer(serializers.ModelSerializer):
    """Serializer for team member skills"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.UUIDField(write_only=True)
    proficiency_label = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = TeamMemberSkill
        fields = [
            'id', 'skill', 'skill_id', 'proficiency_level', 'proficiency_label',
            'years_of_experience', 'is_certified', 'certification_details',
            'last_used', 'notes', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']

class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education records"""
    degree_type_label = serializers.CharField(source='get_degree_type_display', read_only=True)
    
    class Meta:
        model = Education
        fields = [
            'id', 'institution_name', 'degree_type', 'degree_type_label',
            'field_of_study', 'start_year', 'end_year', 'is_current',
            'gpa', 'achievements', 'location', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for certifications"""
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'issuing_organization', 'credential_id', 'issue_date',
            'expiration_date', 'is_active', 'verification_url', 'certificate_image',
            'description', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TeamProjectSerializer(serializers.ModelSerializer):
    """Serializer for team projects"""
    team_size = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamProject
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'is_active',
            'client_name', 'project_value', 'team_size', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_team_size(self, obj):
        """Get count of team members assigned to this project"""
        return obj.team_assignments.filter(is_active=True).count()

class TeamMemberProjectSerializer(serializers.ModelSerializer):
    """Serializer for team member project assignments"""
    project = TeamProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    role_label = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = TeamMemberProject
        fields = [
            'id', 'project', 'project_id', 'role', 'role_label', 'start_date',
            'end_date', 'hours_allocated', 'responsibilities', 'achievements',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    achievement_type_label = serializers.CharField(source='get_achievement_type_display', read_only=True)
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'title', 'achievement_type', 'achievement_type_label',
            'description', 'issuing_organization', 'achievement_date',
            'verification_url', 'image', 'is_featured', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for team relations"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class TeamMemberListSerializer(serializers.ModelSerializer):
    """Serializer for team member list view (minimal data)"""
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    employment_status_label = serializers.CharField(source='get_employment_status_display', read_only=True)
    experience_level_label = serializers.CharField(source='get_experience_level_display', read_only=True)
    key_skills = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'full_name', 'profile_image', 'tagline', 'department_name',
            'position_title', 'employment_status', 'employment_status_label',
            'experience_level', 'experience_level_label', 'years_of_experience',
            'office_location', 'country', 'is_remote', 'is_featured',
            'is_public_profile', 'is_available_for_projects', 'projects_completed',
            'client_rating', 'key_skills', 'created_at', 'updated_at'
        ]
    
    def get_key_skills(self, obj):
        """Get top 5 skills with highest proficiency"""
        skills = obj.member_skills.select_related('skill').order_by('-proficiency_level')[:5]
        return [{'name': skill.skill.name, 'level': skill.proficiency_level} for skill in skills]

class TeamMemberDetailSerializer(serializers.ModelSerializer):
    """Serializer for team member detail view (complete data)"""
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    reports_to = serializers.StringRelatedField(read_only=True)
    reports_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    # Related objects
    member_skills = TeamMemberSkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    project_assignments = TeamMemberProjectSerializer(many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    
    # Computed fields
    full_name = serializers.ReadOnlyField()
    is_active_employee = serializers.ReadOnlyField()
    
    # Labels
    employment_status_label = serializers.CharField(source='get_employment_status_display', read_only=True)
    experience_level_label = serializers.CharField(source='get_experience_level_display', read_only=True)
    
    # Statistics
    total_skills = serializers.SerializerMethodField()
    total_certifications = serializers.SerializerMethodField()
    active_projects = serializers.SerializerMethodField()
    direct_reports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'profile_image', 'bio', 'tagline',
            'department', 'department_id', 'position', 'position_id', 'employment_status',
            'employment_status_label', 'experience_level', 'experience_level_label',
            'hire_date', 'termination_date', 'years_of_experience', 'previous_companies',
            'work_phone', 'work_email', 'linkedin_profile', 'github_profile',
            'portfolio_website', 'office_location', 'country', 'timezone', 'is_remote',
            'reports_to', 'reports_to_id', 'is_featured', 'is_public_profile',
            'is_available_for_projects', 'projects_completed', 'client_rating',
            'full_name', 'is_active_employee', 'total_skills', 'total_certifications',
            'active_projects', 'direct_reports_count', 'member_skills', 'education',
            'certifications', 'project_assignments', 'achievements',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_skills(self, obj):
        """Get total number of skills"""
        return obj.member_skills.count()
    
    def get_total_certifications(self, obj):
        """Get total number of active certifications"""
        return obj.certifications.filter(is_active=True).count()
    
    def get_active_projects(self, obj):
        """Get number of active projects"""
        return obj.project_assignments.filter(is_active=True).count()
    
    def get_direct_reports_count(self, obj):
        """Get number of direct reports"""
        return obj.direct_reports.filter(employment_status__in=['full_time', 'part_time', 'contract']).count()

class TeamMemberCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating team members"""
    
    class Meta:
        model = TeamMember
        fields = [
            'employee_id', 'profile_image', 'bio', 'tagline', 'department_id',
            'position_id', 'employment_status', 'experience_level', 'hire_date',
            'termination_date', 'years_of_experience', 'previous_companies',
            'work_phone', 'work_email', 'linkedin_profile', 'github_profile',
            'portfolio_website', 'office_location', 'country', 'timezone',
            'is_remote', 'reports_to_id', 'is_featured', 'is_public_profile',
            'is_available_for_projects', 'projects_completed', 'client_rating'
        ]
    
    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value < 0 or value > 70:
            raise serializers.ValidationError("Years of experience must be between 0 and 70.")
        return value
    
    def validate_client_rating(self, value):
        """Validate client rating"""
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError("Client rating must be between 0 and 5.")
        return value

class TeamStatsSerializer(serializers.Serializer):
    """Serializer for team statistics"""
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    departments_count = serializers.IntegerField()
    positions_count = serializers.IntegerField()
    members_by_department = serializers.DictField()
    members_by_position = serializers.DictField()
    members_by_experience = serializers.DictField()
    members_by_location = serializers.DictField()
    average_experience_years = serializers.FloatField()
    total_skills = serializers.IntegerField()
    total_certifications = serializers.IntegerField()
    featured_members_count = serializers.IntegerField()
    remote_members_count = serializers.IntegerField()

class TeamSearchSerializer(serializers.Serializer):
    """Serializer for team search parameters"""
    search = serializers.CharField(required=False, help_text="Search in name, bio, tagline")
    department = serializers.UUIDField(required=False, help_text="Filter by department ID")
    position = serializers.UUIDField(required=False, help_text="Filter by position ID")
    employment_status = serializers.ChoiceField(choices=TeamMember._meta.get_field('employment_status').choices, required=False)
    experience_level = serializers.ChoiceField(choices=TeamMember._meta.get_field('experience_level').choices, required=False)
    skill = serializers.UUIDField(required=False, help_text="Filter by skill ID")
    min_experience_years = serializers.IntegerField(required=False)
    max_experience_years = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    is_remote = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)
    is_available = serializers.BooleanField(required=False)
    has_certifications = serializers.BooleanField(required=False)
    min_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    reports_to = serializers.UUIDField(required=False, help_text="Filter by manager ID")