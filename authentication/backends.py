"""
Email Authentication Backend for Rejlers User System
Allows authentication using email address instead of username
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email first, then by username if provided
            user = User.objects.get(
                Q(email=username) | Q(username=username) if username else Q(email=kwargs.get('email', ''))
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple users found, get the first active one
            user = User.objects.filter(
                Q(email=username) | Q(username=username) if username else Q(email=kwargs.get('email', ''))
            ).filter(is_active=True).first()
            if not user:
                return None
        
        # Check if the password is correct and user is active
        if user and user.check_password(password) and user.is_active:
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None