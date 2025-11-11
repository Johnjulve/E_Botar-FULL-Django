from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import ElectionResult, ResultChart, ResultExport, ResultAnalytics, ResultSnapshot
from E_Botar.utils.logging_utils import log_activity


@receiver(post_save, sender=ElectionResult)
def log_election_result_created(sender, instance, created, **kwargs):
    """Log when an election result is created"""
    if created:
        log_activity(
            user=None,  # System action
            action='election_result_created',
            description=f'Result created for {instance.candidate.user.username} in {instance.position.name}'
        )


@receiver(post_save, sender=ResultChart)
def log_result_chart_created(sender, instance, created, **kwargs):
    """Log when a result chart is created"""
    if created:
        log_activity(
            user=instance.created_by,
            action='result_chart_created',
            description=f'Chart created: {instance.title}'
        )


@receiver(post_save, sender=ResultExport)
def log_result_export_created(sender, instance, created, **kwargs):
    """Log when results are exported"""
    if created:
        log_activity(
            user=instance.exported_by,
            action='result_export_created',
            description=f'Results exported: {instance.export_format}'
        )


@receiver(post_save, sender=ResultAnalytics)
def log_result_analytics_created(sender, instance, created, **kwargs):
    """Log when result analytics are created"""
    if created:
        log_activity(
            user=None,  # System action
            action='result_analytics_created',
            description=f'Analytics created: {instance.metric_name}'
        )


@receiver(post_save, sender=ResultSnapshot)
def log_result_snapshot_created(sender, instance, created, **kwargs):
    """Log when a result snapshot is created"""
    if created:
        log_activity(
            user=None,  # System action
            action='result_snapshot_created',
            description=f'Snapshot created for {instance.election.title}'
        )
