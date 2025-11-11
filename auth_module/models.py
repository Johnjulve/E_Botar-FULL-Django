from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import random
import string
from datetime import datetime


class Department(models.Model):
    """Department model for organizing courses"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short department code (e.g., 'CS', 'ENG')")
    description = models.TextField(blank=True, help_text="Optional description of the department")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class Course(models.Model):
    """Course model linked to departments"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, help_text="Course code (e.g., 'CS101', 'ENG201')")
    description = models.TextField(blank=True, help_text="Optional course description")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.department.name}"
    
    class Meta:
        ordering = ['department__name', 'name']
        unique_together = ['department', 'code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class UserProfile(models.Model):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{5}$',
                message='Student ID must be in format XXXX-XXXXX where XXXX is year created and XXXXX is random/indexed (e.g., 2024-12345)',
                code='invalid_student_id'
            )
        ],
        help_text='Format: XXXX-XXXXX where XXXX is year created and XXXXX is random/indexed (e.g., 2024-12345)'
    )
    course_text = models.CharField(max_length=100, blank=True, help_text="Legacy course field - will be migrated")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year_level = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    @classmethod
    def generate_student_id(cls, year=None):
        """
        Generate a unique student ID in format XXXX-XXXXX
        where XXXX is the year created and XXXXX is random/indexed
        
        Args:
            year (int): Year to use for the ID. If None, uses current year.
            
        Returns:
            str: Generated student ID
        """
        if year is None:
            year = datetime.now().year
        
        # Ensure year is 4 digits
        year_str = str(year).zfill(4)
        
        # Generate random 5-digit number
        random_part = random.randint(10000, 99999)
        
        # Create the student ID
        student_id = f"{year_str}-{random_part}"
        
        # Check if this ID already exists
        while cls.objects.filter(student_id=student_id).exists():
            random_part = random.randint(10000, 99999)
            student_id = f"{year_str}-{random_part}"
        
        return student_id

    def clean(self):
        """Custom validation for the model"""
        super().clean()
        
        # Validate student_id format if provided
        if self.student_id:
            # Check if the year part is reasonable (not in the future)
            try:
                year_part = int(self.student_id.split('-')[0])
                current_year = datetime.now().year
                if year_part > current_year:
                    raise ValidationError({
                        'student_id': 'Year in student ID cannot be in the future.'
                    })
                if year_part < 2000:  # Assuming system started around 2000
                    raise ValidationError({
                        'student_id': 'Year in student ID must be 2000 or later.'
                    })
            except (ValueError, IndexError):
                raise ValidationError({
                    'student_id': 'Invalid student ID format.'
                })

    def save(self, *args, **kwargs):
        """Override save to generate student_id if not provided"""
        if not self.student_id:
            self.student_id = self.generate_student_id()
        self.clean()
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    """Model for tracking all system activities and user actions"""
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('register', 'User Registration'),
        ('vote', 'Vote Cast'),
        ('timeout', 'User Timeout'),
        ('create_poll', 'Poll Created'),
        ('create_election', 'Election Created'),
        ('create_candidate', 'Candidate Created'),
        ('update_profile', 'Profile Updated'),
        ('admin_action', 'Admin Action'),
        ('system_action', 'System Action'),
        ('error', 'Error Occurred'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        user_info = self.user.username if self.user else 'Anonymous'
        return f"{user_info} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __init__(self, *args, **kwargs):
        # Support legacy keyword 'action_type' by mapping it to 'action'
        action_type = kwargs.pop('action_type', None)
        if action_type is not None and 'action' not in kwargs:
            kwargs['action'] = action_type
        super().__init__(*args, **kwargs)

    @property
    def action_type(self):
        # Legacy compatibility for tests expecting 'action_type'
        return self.action
