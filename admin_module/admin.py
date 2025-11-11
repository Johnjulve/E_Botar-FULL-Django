from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from auth_module.models import UserProfile, Department, Course, ActivityLog
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party
from voting_module.models import SchoolVote, VoteReceipt

# Avoid double-registration when modules already register their models
for _model in [
    Department,
    Course,
    ActivityLog,
    UserProfile,
    Candidate,
    CandidateApplication,
    SchoolElection,
    SchoolPosition,
    Party,
    SchoolVote,
    VoteReceipt,
]:
    if _model in admin.site._registry:
        admin.site.unregister(_model)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'department', 'course', 'year_level', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'department', 'course', 'year_level', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'student_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id', 'is_verified')
        }),
        ('Academic Information', {
            'fields': ('department', 'course', 'year_level')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'avatar')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'department', 'course')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Department Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('department', 'name', 'code', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action_type', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['user', 'party', 'is_active', 'created_at']
    list_filter = ['is_active', 'party', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Candidate Information', {
            'fields': ('user', 'party', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'party')


@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'status', 'submitted_at']
    list_filter = ['status', 'position', 'submitted_at']
    search_fields = ['user__username', 'position__name']
    readonly_fields = ['submitted_at']
    
    fieldsets = (
        ('Application Information', {
            'fields': ('user', 'position', 'election', 'party', 'status')
        }),
        ('Application Details', {
            'fields': ('manifesto', 'photo', 'review_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Metadata', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('candidate', 'position')


@admin.register(SchoolElection)
class SchoolElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Election Information', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(SchoolPosition)
class SchoolPositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Position Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
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
    list_display = ['user', 'election', 'receipt_code', 'created_at']
    list_filter = ['election', 'created_at']
    search_fields = ['user__username', 'receipt_code']
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
