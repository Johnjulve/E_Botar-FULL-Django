from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def google_oauth_enabled():
    """Check if Google OAuth is enabled"""
    return getattr(settings, 'GOOGLE_OAUTH_ENABLED', False)

@register.simple_tag
def google_login_url():
    """Get Google login URL if enabled, otherwise return #"""
    if getattr(settings, 'GOOGLE_OAUTH_ENABLED', False):
        return '/accounts/google/login/'
    return '#'
