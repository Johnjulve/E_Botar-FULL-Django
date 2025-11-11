from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SecurityEvent, SecurityLog, AccessAttempt, BlockedIP, SecurityAlert
from E_Botar.utils.logging_utils import log_activity


@receiver(post_save, sender=SecurityEvent)
def log_security_event_created(sender, instance, created, **kwargs):
    """Log when a security event is created"""
    if created:
        log_activity(
            user=instance.user,
            action='security_event_created',
            description=f'Security event created: {instance.event_type}',
            request=None,
            additional_data={'ip': instance.ip_address}
        )


@receiver(post_save, sender=SecurityLog)
def log_security_log_created(sender, instance, created, **kwargs):
    """Log when a security log is created"""
    if created:
        log_activity(
            user=instance.user,
            action='security_log_created',
            description=f'Security log created: {instance.level}',
            request=None,
            additional_data={'ip': instance.ip_address}
        )


@receiver(post_save, sender=AccessAttempt)
def log_access_attempt(sender, instance, created, **kwargs):
    """Log when an access attempt is made"""
    if created:
        action = 'successful_login' if instance.success else 'failed_login'
        log_activity(
            user=instance.user,
            action=action,
            description=f'Access attempt: {instance.username}',
            request=None,
            additional_data={'ip': instance.ip_address}
        )


@receiver(post_save, sender=BlockedIP)
def log_ip_blocked(sender, instance, created, **kwargs):
    """Log when an IP is blocked"""
    if created:
        log_activity(
            user=instance.blocked_by,
            action='ip_blocked',
            description=f'IP address blocked: {instance.ip_address}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=SecurityAlert)
def log_security_alert_created(sender, instance, created, **kwargs):
    """Log when a security alert is created"""
    if created:
        log_activity(
            user=None,  # System alert
            action='security_alert_created',
            description=f'Security alert created: {instance.title}',
            request=None,
            additional_data=None
        )


@receiver(post_save, sender=SecurityAlert)
def log_security_alert_resolved(sender, instance, created, **kwargs):
    """Log when a security alert is resolved"""
    if not created and instance.is_resolved:
        log_activity(
            user=instance.resolved_by,
            action='security_alert_resolved',
            description=f'Security alert resolved: {instance.title}',
            request=None,
            additional_data=None
        )
