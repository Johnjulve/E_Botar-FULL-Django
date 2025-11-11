from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SecurityEvent(models.Model):
    """Model for security events"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('login_attempt', 'Login Attempt'),
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('data_breach', 'Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('ip_blocked', 'IP Blocked'),
        ('ip_unblocked', 'IP Unblocked'),
        ('password_change', 'Password Change'),
        ('account_locked', 'Account Locked'),
        ('admin_action', 'Admin Action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Security Event'
        verbose_name_plural = 'Security Events'
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} ({self.created_at})"


class SecurityLog(models.Model):
    """Model for security logs"""
    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Security Log'
        verbose_name_plural = 'Security Logs'
    
    def __str__(self):
        return f"{self.level} - {self.message[:50]}... ({self.timestamp})"


class AccessAttempt(models.Model):
    """Model for tracking access attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150, blank=True)
    success = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Access Attempt'
        verbose_name_plural = 'Access Attempts'
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} ({self.timestamp})"


class SecuritySettings(models.Model):
    """Model for security settings"""
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Security Setting'
        verbose_name_plural = 'Security Settings'
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class BlockedIP(models.Model):
    """Model for blocked IP addresses"""
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField()
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-blocked_at']
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"


class SecurityAlert(models.Model):
    """Model for security alerts"""
    ALERT_TYPE_CHOICES = [
        ('threat_detected', 'Threat Detected'),
        ('anomaly_detected', 'Anomaly Detected'),
        ('policy_violation', 'Policy Violation'),
        ('system_compromise', 'System Compromise'),
    ]
    
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SecurityEvent.SEVERITY_CHOICES)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Security Alert'
        verbose_name_plural = 'Security Alerts'
    
    def __str__(self):
        return f"{self.alert_type} - {self.title}"
