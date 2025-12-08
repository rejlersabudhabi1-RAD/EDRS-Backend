from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import RejlersUser, UserProfile, LoginHistory


class RejlersTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer for Rejlers authentication
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields.pop('username', None)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['employee_id'] = user.employee_id
        token['department'] = user.department
        token['office_location'] = user.office_location
        token['is_team_lead'] = user.is_team_lead
        token['is_project_manager'] = user.is_project_manager
        
        return token
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = RejlersUser
        fields = ('email', 'username', 'first_name', 'last_name', 
                 'password', 'password_confirm', 'department', 'position', 
                 'phone', 'office_location')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = RejlersUser.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.ReadOnlyField()
    office_display_name = serializers.ReadOnlyField(source='get_office_display_name')
    
    class Meta:
        model = RejlersUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                 'full_name', 'employee_id', 'department', 'position', 
                 'phone', 'office_location', 'office_display_name', 'bio', 
                 'profile_picture', 'date_joined', 'is_verified', 
                 'is_team_lead', 'is_project_manager')
        read_only_fields = ('id', 'email', 'date_joined', 'is_verified')


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer including profile data
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for login history
    """
    user_name = serializers.ReadOnlyField(source='user.full_name')
    
    class Meta:
        model = LoginHistory
        fields = ('id', 'user_name', 'ip_address', 'login_time', 
                 'logout_time', 'is_successful')
        read_only_fields = '__all__'


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            user = RejlersUser.objects.get(email=value)
            return value
        except RejlersUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs