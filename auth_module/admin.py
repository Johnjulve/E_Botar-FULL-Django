from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Department, Course, ActivityLog


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_student_id', 'get_department', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__is_verified', 'profile__department')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__student_id')
    
    def get_student_id(self, instance):
        return instance.profile.student_id if hasattr(instance, 'profile') else '-'
    get_student_id.short_description = 'Student ID'
    
    def get_department(self, instance):
        return instance.profile.department.name if hasattr(instance, 'profile') and instance.profile.department else '-'
    get_department.short_description = 'Department'
    
    def is_verified(self, instance):
        return instance.profile.is_verified if hasattr(instance, 'profile') else False
    is_verified.boolean = True
    is_verified.short_description = 'Verified'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('name', 'code', 'department__name')
    ordering = ('department', 'name')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address', 'user_agent')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'user__email', 'action')
    readonly_fields = ('timestamp', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
