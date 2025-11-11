from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ElectionResult, ResultChart, ResultExport, ResultAnalytics, ResultSnapshot


@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = ['election', 'position', 'candidate', 'vote_count', 'percentage', 'created_at']
    list_filter = ['election', 'position', 'created_at']
    search_fields = ['election__title', 'position__name', 'candidate__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Result Information', {
            'fields': ('election', 'position', 'candidate')
        }),
        ('Vote Data', {
            'fields': ('vote_count', 'percentage')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'election', 'position', 'candidate__user'
        )


@admin.register(ResultChart)
class ResultChartAdmin(admin.ModelAdmin):
    list_display = ['title', 'election', 'position', 'chart_type', 'is_active', 'created_at']
    list_filter = ['chart_type', 'is_active', 'election', 'created_at']
    search_fields = ['title', 'description', 'election__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Chart Information', {
            'fields': ('election', 'position', 'chart_type', 'title', 'description')
        }),
        ('Configuration', {
            'fields': ('config', 'order', 'is_active')
        }),
        ('Administration', {
            'fields': ('created_by', 'created_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'election', 'position', 'created_by'
        )


@admin.register(ResultExport)
class ResultExportAdmin(admin.ModelAdmin):
    list_display = ['election', 'export_format', 'file_size', 'exported_by', 'exported_at']
    list_filter = ['export_format', 'exported_at']
    search_fields = ['election__title', 'exported_by__username']
    readonly_fields = ['exported_at']
    date_hierarchy = 'exported_at'
    
    fieldsets = (
        ('Export Information', {
            'fields': ('election', 'export_format')
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size')
        }),
        ('Administration', {
            'fields': ('exported_by', 'exported_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('election', 'exported_by')


@admin.register(ResultAnalytics)
class ResultAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['election', 'position', 'metric_name', 'metric_value', 'calculated_at']
    list_filter = ['metric_name', 'election', 'calculated_at']
    search_fields = ['election__title', 'position__name', 'metric_name']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'calculated_at'
    
    fieldsets = (
        ('Analytics Information', {
            'fields': ('election', 'position', 'metric_name', 'metric_value')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Metadata', {
            'fields': ('calculated_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('election', 'position')


@admin.register(ResultSnapshot)
class ResultSnapshotAdmin(admin.ModelAdmin):
    list_display = ['election', 'total_votes', 'total_voters', 'participation_rate', 'created_at']
    list_filter = ['election', 'created_at']
    search_fields = ['election__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Snapshot Information', {
            'fields': ('election', 'total_votes', 'total_voters', 'participation_rate')
        }),
        ('Data', {
            'fields': ('snapshot_data',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('election')
