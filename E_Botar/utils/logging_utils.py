"""
Consolidated logging utilities for E-Botar system
"""
import json
import logging
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

# Import models (will be updated when modules are consolidated)
try:
    from auth_module.models import ActivityLog
except ImportError:
    # Fallback for current structure
    from users.models import ActivityLog

logger = logging.getLogger(__name__)


def log_activity(user, action, description, request=None, additional_data=None):
    """
    Log user activity to the database
    
    Args:
        user: User object (can be AnonymousUser)
        action: Type of action (from ActivityLog.ACTION_TYPES)
        description: Human-readable description
        request: Django request object (optional)
        additional_data: Additional data as dict (optional)
    """
    try:
        # Handle anonymous users
        user_obj = user if user and not isinstance(user, AnonymousUser) else None
        
        # Extract request information
        ip_address = None
        user_agent = ''
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create activity log entry
        ActivityLog.objects.create(
            user=user_obj,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=additional_data or {}
        )
    except Exception as e:
        # Log the error but don't break the main functionality
        logger.error(f"Error logging activity: {str(e)}")


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_login(user, request=None):
    """Log user login activity"""
    log_activity(
        user=user,
        action='login',
        description=f"User {user.username} logged in successfully",
        request=request
    )


def log_user_logout(user, request=None):
    """Log user logout activity"""
    log_activity(
        user=user,
        action='logout',
        description=f"User {user.username} logged out",
        request=request
    )


def log_user_registration(user, request=None):
    """Log user registration activity"""
    log_activity(
        user=user,
        action='register',
        description=f"New user {user.username} registered successfully",
        request=request
    )


def log_user_timeout(user, idle_minutes: int, request=None):
    """Log user inactivity timeout event (session idle)."""
    log_activity(
        user=user,
        action='timeout',
        description=f"User {user.username} timed out after {idle_minutes} minutes of inactivity",
        request=request,
        additional_data={
            'idle_minutes': idle_minutes,
        }
    )


def log_vote_cast(user, candidate, election, request=None):
    """Log vote casting activity"""
    log_activity(
        user=user,
        action='vote',
        description=f"User {user.username} voted for {candidate.user.get_full_name()} in {election.title}",
        request=request,
        additional_data={
            'candidate_id': candidate.id,
            'election_id': election.id,
            'position': candidate.position.name
        }
    )


def log_admin_action(user, action, description, request=None, additional_data=None):
    """Log admin action"""
    log_activity(
        user=user,
        action='admin_action',
        description=f"Admin {user.username}: {description}",
        request=request,
        additional_data=additional_data or {}
    )


def log_system_action(action, description, request=None, additional_data=None):
    """Log system action"""
    log_activity(
        user=None,
        action='system_action',
        description=description,
        request=request,
        additional_data=additional_data or {}
    )


def log_error(user, error_message, request=None, additional_data=None):
    """Log error occurrence"""
    log_activity(
        user=user,
        action='error',
        description=f"Error: {error_message}",
        request=request,
        additional_data=additional_data or {}
    )


def log_election_created(user, election, request=None):
    """Log election creation"""
    log_activity(
        user=user,
        action='create_election',
        description=f"Election '{election.title}' created",
        request=request,
        additional_data={
            'election_id': election.id,
            'start_date': election.start_date.isoformat(),
            'end_date': election.end_date.isoformat()
        }
    )


def log_candidate_application(user, application, request=None):
    """Log candidate application"""
    log_activity(
        user=user,
        action='create_candidate',
        description=f"Candidate application submitted for {application.position.name}",
        request=request,
        additional_data={
            'application_id': application.id,
            'position_id': application.position.id,
            'election_id': application.election.id
        }
    )


def log_profile_update(user, request=None):
    """Log profile update"""
    log_activity(
        user=user,
        action='update_profile',
        description=f"User {user.username} updated their profile",
        request=request
    )


def get_activity_summary(days=7):
    """Get activity summary for the last N days"""
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    
    activities = ActivityLog.objects.filter(
        timestamp__gte=start_date
    ).values('action').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    return list(activities)


def get_user_activity(user, days=30):
    """Get user activity for the last N days"""
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    
    return ActivityLog.objects.filter(
        user=user,
        timestamp__gte=start_date
    ).order_by('-timestamp')


def cleanup_old_logs(days=90):
    """Clean up old activity logs"""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    deleted_count = ActivityLog.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old activity logs")
    return deleted_count
