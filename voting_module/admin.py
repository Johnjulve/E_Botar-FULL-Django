from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count

from .models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot


@admin.register(SchoolVote)
class SchoolVoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'position', 'election', 'receipt_code', 'created_at']
    list_filter = ['election', 'position', 'created_at']
    search_fields = ['voter__username', 'candidate__user__username', 'receipt_code']
    readonly_fields = ['created_at', 'receipt_code']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Vote Information', {
            'fields': ('voter', 'candidate', 'position', 'election')
        }),
        ('Receipt Information', {
            'fields': ('receipt_code', 'encrypted_receipt_code')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'voter', 'candidate', 'position', 'election'
        )


@admin.register(VoteReceipt)
class VoteReceiptAdmin(admin.ModelAdmin):
    list_display = ['voter', 'election', 'receipt_code', 'created_at']
    list_filter = ['election', 'created_at']
    search_fields = ['voter__username', 'receipt_code']
    readonly_fields = ['created_at', 'receipt_code', 'encrypted_receipt_code']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Receipt Information', {
            'fields': ('voter', 'election', 'receipt_code')
        }),
        ('Security', {
            'fields': ('encrypted_receipt_code',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('voter', 'election')


@admin.register(AnonVote)
class AnonVoteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'position', 'election', 'created_at']
    list_filter = ['election', 'position', 'created_at']
    search_fields = ['candidate__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Anonymous Vote Information', {
            'fields': ('candidate', 'position', 'election')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate', 'position', 'election'
        )


@admin.register(EncryptedBallot)
class EncryptedBallotAdmin(admin.ModelAdmin):
    list_display = ['election', 'encrypted_data_preview', 'created_at']
    list_filter = ['election', 'created_at']
    search_fields = ['election__title']
    readonly_fields = ['created_at', 'encrypted_data_preview']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Encrypted Ballot Information', {
            'fields': ('election', 'encrypted_data')
        }),
        ('Preview', {
            'fields': ('encrypted_data_preview',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def encrypted_data_preview(self, obj):
        if obj.encrypted_data:
            preview = obj.encrypted_data[:50] + "..." if len(obj.encrypted_data) > 50 else obj.encrypted_data
            return format_html('<code>{}</code>', preview)
        return '-'
    encrypted_data_preview.short_description = 'Encrypted Data Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('election')
