from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from E_Botar.utils.logging_utils import log_activity


@receiver(post_save, sender=SchoolVote)
def log_vote_created(sender, instance, created, **kwargs):
    """Log when a vote is created"""
    if created:
        log_activity(
            user=instance.voter,
            action='vote_submitted',
            description=f'Voted for {instance.candidate.user.username} for {instance.position.name}'
        )


@receiver(post_save, sender=VoteReceipt)
def log_receipt_created(sender, instance, created, **kwargs):
    """Log when a vote receipt is created"""
    if created:
        log_activity(
            user=instance.user,
            action='receipt_generated',
            description=f'Generated receipt {instance.receipt_code} for election: {instance.election.title}'
        )


@receiver(post_save, sender=AnonVote)
def log_anon_vote_created(sender, instance, created, **kwargs):
    """Log when an anonymous vote is created"""
    if created:
        log_activity(
            user=None,  # Anonymous vote
            action='anon_vote_submitted',
            description=f'Anonymous vote for {instance.candidate.user.username} for {instance.position.name}'
        )


@receiver(post_save, sender=EncryptedBallot)
def log_encrypted_ballot_created(sender, instance, created, **kwargs):
    """Log when an encrypted ballot is created"""
    if created:
        log_activity(
            user=None,  # System action
            action='encrypted_ballot_created',
            description=f'Created encrypted ballot for election: {instance.election.title}'
        )
