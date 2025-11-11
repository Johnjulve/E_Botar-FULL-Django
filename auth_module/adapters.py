from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from .models import UserProfile, Department, Course
import random
from datetime import datetime


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle Google OAuth integration with UserProfile"""
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login"""
        # Get the user's email from Google
        email = sociallogin.account.extra_data.get('email')
        if email:
            # Check if user already exists
            try:
                existing_user = User.objects.get(email=email)
                # Link the social account to existing user
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                # User doesn't exist, will be created by allauth
                pass
    
    def populate_user(self, request, sociallogin, data):
        """Populate user data from Google"""
        user = super().populate_user(request, sociallogin, data)
        
        # Get Google profile data
        google_data = sociallogin.account.extra_data
        
        # Update user data from Google
        user.first_name = google_data.get('given_name', '')
        user.last_name = google_data.get('family_name', '')
        user.email = google_data.get('email', '')
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Save user and create UserProfile"""
        user = super().save_user(request, sociallogin, form)
        
        # Create UserProfile for the new user
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # Generate a student ID for the new user
            student_id = UserProfile.generate_student_id()
            
            # Create UserProfile
            profile = UserProfile.objects.create(
                user=user,
                student_id=student_id,
                is_verified=True,  # Google users are pre-verified
                phone_number='',
                year_level=''
            )
        
        return user
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """Allow automatic signup for Google users"""
        return True
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting social account"""
        return '/auth/profile/'  # Redirect to profile to complete setup
