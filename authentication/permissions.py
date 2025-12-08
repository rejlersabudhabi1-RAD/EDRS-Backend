from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` or related owner field.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        # Check different possible owner fields
        if hasattr(obj, 'created_by') and obj.created_by:
            return obj.created_by == request.user
        elif hasattr(obj, 'user') and obj.user:
            return obj.user == request.user
        elif hasattr(obj, 'owner') and obj.owner:
            return obj.owner == request.user
        elif hasattr(obj, 'uploaded_by') and obj.uploaded_by:
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'team_member') and obj.team_member:
            # For team member related objects, check if user is the team member's user
            return obj.team_member.user == request.user
        
        # If no owner field found, allow staff users to modify
        return request.user.is_staff

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners or staff members to access an object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff users have full access
        if request.user.is_staff:
            return True
            
        # Check different possible owner fields
        if hasattr(obj, 'created_by') and obj.created_by:
            return obj.created_by == request.user
        elif hasattr(obj, 'user') and obj.user:
            return obj.user == request.user
        elif hasattr(obj, 'owner') and obj.owner:
            return obj.owner == request.user
        elif hasattr(obj, 'uploaded_by') and obj.uploaded_by:
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'team_member') and obj.team_member:
            # For team member related objects, check if user is the team member's user
            return obj.team_member.user == request.user
            
        return False

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff to create/edit objects.
    Read access is allowed for everyone.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to staff users.
        return request.user and request.user.is_staff

class IsOwnerProfileOrReadOnly(permissions.BasePermission):
    """
    Custom permission for user profiles.
    Users can only edit their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the profile owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If the object itself is the user
        return obj == request.user

class IsTeamMemberOrReadOnly(permissions.BasePermission):
    """
    Custom permission for team member objects.
    Team members can only edit their own profile and related objects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Staff users have full access
        if request.user.is_staff:
            return True
        
        # Check if user is the team member
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'team_member'):
            return obj.team_member.user == request.user
        
        return False

class IsAssignedToOrStaff(permissions.BasePermission):
    """
    Custom permission for objects assigned to users (like inquiries).
    Users can only access objects assigned to them, staff can access all.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff users have full access
        if request.user.is_staff:
            return True
        
        # Check if object is assigned to the user
        if hasattr(obj, 'assigned_to') and obj.assigned_to:
            return obj.assigned_to == request.user
        
        return False