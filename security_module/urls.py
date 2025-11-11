from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'security_module'

urlpatterns = [
    # Security Dashboard
    path('', views.security_dashboard, name='security_dashboard'),
    
    # Security Monitoring
    path('events/', views.security_events, name='security_events'),
    path('access-attempts/', views.access_attempts, name='access_attempts'),
    path('logs/', views.security_logs, name='security_logs'),
    
    # Security Management
    path('settings/', views.security_settings, name='security_settings'),
    path('report/', views.security_report, name='security_report'),
    path('threat-detection/', views.threat_detection, name='threat_detection'),
    
    # Security Actions
    path('block-ip/', views.block_ip, name='block_ip'),
    path('unblock-ip/', views.unblock_ip, name='unblock_ip'),
    
    # User Security
    path('my-security/', views.user_security_status, name='user_security_status'),
    
    # Activity logs redirect (for backward compatibility)
    path('activity-logs/', lambda request: redirect('/admin-ui/activity-logs/'), name='activity_logs'),
]
