from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import SecurityEvent, SecurityLog, AccessAttempt, SecuritySettings, BlockedIP, SecurityAlert


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'severity', 'user', 'ip_address', 'created_at']
    list_filter = ['event_type', 'severity', 'created_at']
    search_fields = ['description', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'severity', 'description')
        }),
        ('Technical Details', {
            'fields': ('user', 'ip_address', 'user_agent', 'metadata')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message_preview', 'user', 'ip_address', 'timestamp']
    list_filter = ['level', 'timestamp']
    search_fields = ['message', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('level', 'message')
        }),
        ('Technical Details', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        })
    )
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AccessAttempt)
class AccessAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'success', 'ip_address', 'timestamp']
    list_filter = ['success', 'timestamp']
    search_fields = ['username', 'ip_address', 'user_agent']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Access Information', {
            'fields': ('user', 'username', 'success')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value_preview', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('name', 'value', 'description')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        })
    )
    
    def value_preview(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason_preview', 'blocked_by', 'blocked_at', 'is_active']
    list_filter = ['is_active', 'blocked_at']
    search_fields = ['ip_address', 'reason']
    readonly_fields = ['blocked_at']
    date_hierarchy = 'blocked_at'
    
    fieldsets = (
        ('Block Information', {
            'fields': ('ip_address', 'reason', 'is_active')
        }),
        ('Administration', {
            'fields': ('blocked_by', 'blocked_at')
        })
    )
    
    def reason_preview(self, obj):
        return obj.reason[:50] + "..." if len(obj.reason) > 50 else obj.reason
    reason_preview.short_description = 'Reason'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blocked_by')


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'title', 'severity', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_resolved', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'title', 'description', 'severity')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resolved_by')
