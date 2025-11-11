"""
Context processors for making data available to all templates
"""
from django.utils import timezone
from election_module.models import SchoolElection


def applications_status(request):
    """
    Check if candidate applications are currently available
    Applications are available only if there are upcoming elections (not started yet)
    """
    now = timezone.now()
    applications_available = SchoolElection.objects.filter(
        is_active=True,
        start_date__gt=now  # Only elections that haven't started yet
    ).exists()
    
    return {
        'applications_available': applications_available,
    }

