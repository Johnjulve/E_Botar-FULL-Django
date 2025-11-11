from django.contrib import admin
from .models import Candidate, CandidateApplication


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'election', 'party', 'is_active', 'created_at')
    list_filter = ('election', 'position', 'party', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position__name')
    ordering = ('election', 'position', 'user__first_name')


@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'election', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'election', 'position', 'submitted_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position__name')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'reviewed_at')
