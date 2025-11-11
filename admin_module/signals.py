from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from auth_module.models import UserProfile, ActivityLog
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party
from voting_module.models import SchoolVote, VoteReceipt
from E_Botar.utils.logging_utils import log_activity


@receiver(post_save, sender=UserProfile)
def log_user_profile_created(sender, instance, created, **kwargs):
    """Log when a user profile is created or updated"""
    if created:
        log_activity(
            user=instance.user,
            action='user_profile_created',
            description=f'User profile created for {instance.user.username}',
            request=None,
            additional_data=None
        )
    else:
        log_activity(
            user=instance.user,
            action='user_profile_updated',
            description=f'User profile updated for {instance.user.username}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=Candidate)
def log_candidate_created(sender, instance, created, **kwargs):
    """Log when a candidate is created or updated"""
    if created:
        log_activity(
            user=instance.user,
            action='candidate_created',
            description=f'Candidate profile created for {instance.user.username}',
            request=None,
            additional_data=None
        )
    else:
        log_activity(
            user=instance.user,
            action='candidate_updated',
            description=f'Candidate profile updated for {instance.user.username}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=CandidateApplication)
def log_application_status_change(sender, instance, created, **kwargs):
    """Log when an application status changes"""
    if not created:  # Only log updates, not creation
        log_activity(
            user=None,  # Admin action
            action='application_status_changed',
            description=f'Application status changed to {instance.status} for {instance.user.username}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=SchoolElection)
def log_election_status_change(sender, instance, created, **kwargs):
    """Log when an election status changes"""
    if not created:  # Only log updates, not creation
        log_activity(
            user=None,  # Admin action
            action='election_status_changed',
            description=f'Election status changed for {instance.title}',
            request=None,
            additional_data=None
        )


@receiver(post_delete, sender=UserProfile)
def log_user_profile_deleted(sender, instance, **kwargs):
    """Log when a user profile is deleted"""
    log_activity(
        user=None,  # Admin action
        action='user_profile_deleted',
        description=f'User profile deleted for {instance.user.username}',
        request=None,
        additional_data=None
    )


@receiver(post_delete, sender=Candidate)
def log_candidate_deleted(sender, instance, **kwargs):
    """Log when a candidate is deleted"""
    log_activity(
        user=None,  # Admin action
        action='candidate_deleted',
        description=f'Candidate profile deleted for {instance.user.username}',
        request=None,
        additional_data=None
    )


@receiver(post_delete, sender=SchoolElection)
def log_election_deleted(sender, instance, **kwargs):
    """Log when an election is deleted"""
    log_activity(
        user=None,  # Admin action
        action='election_deleted',
        description=f'Election deleted: {instance.title}',
        request=None,
        additional_data=None
    )
