from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import SchoolElection, SchoolPosition, Party
from E_Botar.utils.logging_utils import log_activity


@receiver(post_save, sender=SchoolElection)
def log_election_created(sender, instance, created, **kwargs):
    """Log when an election is created or updated"""
    if created:
        log_activity(
            user=instance.created_by,
            action='election_created',
            description=f'Created election: {instance.title}',
            request=None,
            additional_data=None
        )
    else:
        log_activity(
            user=instance.created_by,
            action='election_updated',
            description=f'Updated election: {instance.title}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=SchoolPosition)
def log_position_created(sender, instance, created, **kwargs):
    """Log when a position is created or updated"""
    if created:
        log_activity(
            user=None,  # System action
            action='position_created',
            description=f'Created position: {instance.name}',
            request=None,
            additional_data=None
        )
    else:
        log_activity(
            user=None,  # System action
            action='position_updated',
            description=f'Updated position: {instance.name}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=Party)
def log_party_created(sender, instance, created, **kwargs):
    """Log when a party is created or updated"""
    if created:
        log_activity(
            user=None,
            action='party_created',
            description=f"Party created: {instance.name}",
            request=None,
            additional_data=None
        )
    else:
        log_activity(
            user=None,  # System action
            action='party_updated',
            description=f'Updated party: {instance.name}',
            request=None,
            additional_data=None
        )


@receiver(post_delete, sender=SchoolElection)
def log_election_deleted(sender, instance, **kwargs):
    """Log when an election is deleted"""
    log_activity(
        user=instance.created_by,
        action='election_deleted',
        description=f'Deleted election: {instance.title}',
        request=None,
        additional_data=None
    )
