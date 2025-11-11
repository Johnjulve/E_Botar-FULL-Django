from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from auth_module.models import UserProfile, ActivityLog
from .models import SecurityEvent, SecurityLog, AccessAttempt
from .forms import SecuritySettingsForm, SecurityEventForm
from E_Botar.utils.logging_utils import log_activity
from E_Botar.services.security import check_security_threats, generate_security_report


@staff_member_required
def security_dashboard(request):
    """Security dashboard for monitoring system security"""
    # Get security statistics
    total_events = SecurityEvent.objects.count()
    critical_events = SecurityEvent.objects.filter(severity='critical').count()
    failed_logins = AccessAttempt.objects.filter(success=False).count()
    suspicious_activities = SecurityEvent.objects.filter(
        severity__in=['high', 'critical']
    ).count()
    
    # Get recent security events
    recent_events = SecurityEvent.objects.select_related('user').order_by('-created_at')[:10]
    
    # Get failed access attempts
    failed_attempts = AccessAttempt.objects.filter(success=False).order_by('-timestamp')[:10]
    
    context = {
        'total_events': total_events,
        'critical_events': critical_events,
        'failed_logins': failed_logins,
        'suspicious_activities': suspicious_activities,
        'recent_events': recent_events,
        'failed_attempts': failed_attempts,
        'page_title': 'Security Dashboard'
    }
    return render(request, 'security_module/security_dashboard.html', context)


@staff_member_required
def security_events(request):
    """Display security events"""
    events = SecurityEvent.objects.select_related('user').order_by('-created_at')
    
    # Filter by severity
    severity_filter = request.GET.get('severity')
    if severity_filter:
        events = events.filter(severity=severity_filter)
    
    # Filter by event type
    event_type_filter = request.GET.get('event_type')
    if event_type_filter:
        events = events.filter(event_type=event_type_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        events = events.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    # Paginate results
    paginator = Paginator(events, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severity_filter': severity_filter,
        'event_type_filter': event_type_filter,
        'search_query': search_query,
        'page_title': 'Security Events'
    }
    return render(request, 'security_module/security_events.html', context)


@staff_member_required
def access_attempts(request):
    """Display access attempts"""
    attempts = AccessAttempt.objects.select_related('user').order_by('-timestamp')
    
    # Filter by success status
    success_filter = request.GET.get('success')
    if success_filter == 'successful':
        attempts = attempts.filter(success=True)
    elif success_filter == 'failed':
        attempts = attempts.filter(success=False)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        attempts = attempts.filter(
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(user_agent__icontains=search_query)
        )
    
    # Paginate results
    paginator = Paginator(attempts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'success_filter': success_filter,
        'search_query': search_query,
        'page_title': 'Access Attempts'
    }
    return render(request, 'security_module/access_attempts.html', context)


@staff_member_required
def security_logs(request):
    """Display security logs"""
    logs = SecurityLog.objects.select_related('user').order_by('-timestamp')
    
    # Filter by log level
    level_filter = request.GET.get('level')
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        logs = logs.filter(
            Q(message__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    # Paginate results
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'level_filter': level_filter,
        'search_query': search_query,
        'page_title': 'Security Logs'
    }
    return render(request, 'security_module/security_logs.html', context)


@staff_member_required
def security_settings(request):
    """Security settings management"""
    if request.method == 'POST':
        form = SecuritySettingsForm(request.POST)
        if form.is_valid():
            # Update security settings
            settings = form.cleaned_data
            
            log_activity(
                user=request.user,
                action_type='security_settings_updated',
                description='Security settings updated',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Security settings updated successfully!')
            return redirect('security_module:security_settings')
    else:
        form = SecuritySettingsForm()
    
    context = {
        'form': form,
        'page_title': 'Security Settings'
    }
    return render(request, 'security_module/security_settings.html', context)


@staff_member_required
def security_report(request):
    """Generate security report"""
    # Get date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        events = SecurityEvent.objects.filter(
            created_at__date__range=[date_from, date_to]
        )
        attempts = AccessAttempt.objects.filter(
            timestamp__date__range=[date_from, date_to]
        )
    else:
        events = SecurityEvent.objects.all()
        attempts = AccessAttempt.objects.all()
    
    # Generate report data
    report_data = generate_security_report(events, attempts)
    
    context = {
        'report_data': report_data,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Security Report'
    }
    return render(request, 'security_module/security_report.html', context)


@staff_member_required
def threat_detection(request):
    """Threat detection and analysis"""
    # Check for security threats
    threats = check_security_threats()
    
    # Get suspicious activities
    suspicious_activities = SecurityEvent.objects.filter(
        severity__in=['high', 'critical']
    ).order_by('-created_at')[:20]
    
    # Get failed login patterns
    failed_logins = AccessAttempt.objects.filter(success=False).values(
        'ip_address'
    ).annotate(
        count=Count('id')
    ).filter(count__gte=5).order_by('-count')
    
    context = {
        'threats': threats,
        'suspicious_activities': suspicious_activities,
        'failed_logins': failed_logins,
        'page_title': 'Threat Detection'
    }
    return render(request, 'security_module/threat_detection.html', context)


@staff_member_required
@require_http_methods(["POST"])
def block_ip(request):
    """Block IP address"""
    ip_address = request.POST.get('ip_address')
    
    if ip_address:
        # Create security event for IP blocking
        SecurityEvent.objects.create(
            event_type='ip_blocked',
            severity='high',
            description=f'IP address {ip_address} blocked by admin',
            ip_address=ip_address,
            user=request.user
        )
        
        log_activity(
            user=request.user,
            action_type='ip_blocked',
            description=f'Blocked IP address: {ip_address}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'IP address {ip_address} blocked successfully!')
    else:
        messages.error(request, 'Invalid IP address.')
    
    return redirect('security_module:threat_detection')


@staff_member_required
@require_http_methods(["POST"])
def unblock_ip(request):
    """Unblock IP address"""
    ip_address = request.POST.get('ip_address')
    
    if ip_address:
        # Create security event for IP unblocking
        SecurityEvent.objects.create(
            event_type='ip_unblocked',
            severity='medium',
            description=f'IP address {ip_address} unblocked by admin',
            ip_address=ip_address,
            user=request.user
        )
        
        log_activity(
            user=request.user,
            action_type='ip_unblocked',
            description=f'Unblocked IP address: {ip_address}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'IP address {ip_address} unblocked successfully!')
    else:
        messages.error(request, 'Invalid IP address.')
    
    return redirect('security_module:threat_detection')


@login_required
def user_security_status(request):
    """Display user's security status"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile to view security status.')
        return redirect('candidate_module:candidate_profile')
    
    # Get user's security events
    user_events = SecurityEvent.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get user's access attempts
    user_attempts = AccessAttempt.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Get user's activity log
    user_activities = ActivityLog.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'user_events': user_events,
        'user_attempts': user_attempts,
        'user_activities': user_activities,
        'page_title': 'My Security Status'
    }
    return render(request, 'security_module/user_security_status.html', context)
