from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import UserProfile


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for anonymous users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip check for admin users
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)

        # Skip check for profile-related pages
        profile_urls = [
            '/auth/profile/',
            '/auth/logout/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(url) for url in profile_urls):
            return self.get_response(request)

        # Check if user has profile
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            messages.warning(request, 'Please complete your profile first.')
            return redirect('auth_module:profile')

        # Check if course and department are selected
        if not profile.course or not profile.department:
            messages.warning(request, 'Please select your course and department in your profile.')
            return redirect('auth_module:profile')

        return self.get_response(request)
