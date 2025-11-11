from django import forms
from django.core.exceptions import ValidationError

from .models import SecurityEvent, SecuritySettings, BlockedIP, SecurityAlert


class SecuritySettingsForm(forms.Form):
    """Form for security settings"""
    
    max_login_attempts = forms.IntegerField(
        min_value=3,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Maximum login attempts before account lockout"
    )
    session_timeout = forms.IntegerField(
        min_value=15,
        max_value=480,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Session timeout in minutes"
    )
    require_strong_password = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Require strong passwords"
    )
    enable_two_factor = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Enable two-factor authentication"
    )
    log_failed_attempts = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Log failed login attempts"
    )
    block_suspicious_ips = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Automatically block suspicious IP addresses"
    )


class SecurityEventForm(forms.ModelForm):
    """Form for creating security events"""
    
    class Meta:
        model = SecurityEvent
        fields = ['event_type', 'severity', 'description', 'ip_address']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BlockedIPForm(forms.ModelForm):
    """Form for blocking IP addresses"""
    
    class Meta:
        model = BlockedIP
        fields = ['ip_address', 'reason']
        widgets = {
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_ip_address(self):
        ip_address = self.cleaned_data.get('ip_address')
        if ip_address:
            # Check if IP is already blocked
            if BlockedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
                raise ValidationError('This IP address is already blocked.')
        return ip_address


class SecurityAlertForm(forms.ModelForm):
    """Form for creating security alerts"""
    
    class Meta:
        model = SecurityAlert
        fields = ['alert_type', 'title', 'description', 'severity']
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
        }


class SecuritySearchForm(forms.Form):
    """Form for searching security events"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by description, IP, or username...'
        })
    )
    severity = forms.ChoiceField(
        choices=[
            ('', 'All Severities'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    event_type = forms.ChoiceField(
        choices=[
            ('', 'All Event Types'),
            ('login_attempt', 'Login Attempt'),
            ('failed_login', 'Failed Login'),
            ('suspicious_activity', 'Suspicious Activity'),
            ('data_breach', 'Data Breach'),
            ('unauthorized_access', 'Unauthorized Access'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
