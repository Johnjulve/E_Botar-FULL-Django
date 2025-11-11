from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import SchoolElection, SchoolPosition, ElectionPosition, Party


@admin.register(SchoolElection)
class SchoolElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    readonly_fields = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Election Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    # No created_by field in model; use default behaviors


@admin.register(SchoolPosition)
class SchoolPositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = []
    
    fieldsets = (
        ('Position Information', {
            'fields': ('name', 'description', 'is_active')
        }),
    )


@admin.register(ElectionPosition)
class ElectionPositionAdmin(admin.ModelAdmin):
    list_display = ['election', 'position', 'order']
    list_filter = ['election', 'position']
    search_fields = ['election__title', 'position__name']
    readonly_fields = []
    
    fieldsets = (
        ('Election Position', {
            'fields': ('election', 'position', 'order')
        }),
    )


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'logo_preview']
    
    fieldsets = (
        ('Party Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Branding', {
            'fields': ('logo', 'logo_preview', 'color')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.logo.url
            )
        return 'No logo uploaded'
    logo_preview.short_description = 'Logo Preview'
