from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(pre_delete, sender=User)
def delete_user_dependents(sender, instance: User, using, **kwargs):
    """Ensure related rows are removed before User deletion.

    This covers deletions triggered from Django admin or anywhere else.
    """
    try:
        # Local imports to avoid circular deps at import time
        from voting_module.models import SchoolVote, VoteReceipt, EncryptedBallot
        from candidate_module.models import CandidateApplication

        SchoolVote.objects.using(using).filter(user=instance).delete()
        VoteReceipt.objects.using(using).filter(user=instance).delete()
        EncryptedBallot.objects.using(using).filter(user=instance).delete()
        CandidateApplication.objects.using(using).filter(user=instance).delete()
    except Exception:
        # Best effort cleanup; the database CASCADE on some relations may still handle it
        pass
