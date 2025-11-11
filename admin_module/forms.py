from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from auth_module.models import UserProfile, Department, Course
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party


class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments"""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS',
                'maxlength': '10'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the department'
            }),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper().strip()
            # Check for duplicate codes
            if self.instance.pk:
                # Editing existing department
                if Department.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                    raise ValidationError('A department with this code already exists.')
            else:
                # Creating new department
                if Department.objects.filter(code=code).exists():
                    raise ValidationError('A department with this code already exists.')
        return code


class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""
    
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Science in Computer Science'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., BSCS',
                'maxlength': '10'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the course'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all().order_by('name')
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper().strip()
            # Check for duplicate codes within the same department
            department = self.cleaned_data.get('department')
            if department:
                if self.instance.pk:
                    # Editing existing course
                    if Course.objects.filter(code=code, department=department).exclude(pk=self.instance.pk).exists():
                        raise ValidationError('A course with this code already exists in this department.')
                else:
                    # Creating new course
                    if Course.objects.filter(code=code, department=department).exists():
                        raise ValidationError('A course with this code already exists in this department.')
        return code


class DepartmentCSVImportForm(forms.Form):
    """Form for importing departments from CSV"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text="Upload a CSV file with columns: name, code, description"
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('Please upload a CSV file.')
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('File size must be less than 5MB.')
        return csv_file


class CourseCSVImportForm(forms.Form):
    """Form for importing courses from CSV"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text="Upload a CSV file with columns: name, code, department_code, description"
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('Please upload a CSV file.')
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('File size must be less than 5MB.')
        return csv_file


class UserCreationForm(forms.ModelForm):
    """Form for creating new users"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Password for the new user"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Confirm the password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for creating user profiles"""
    
    class Meta:
        model = UserProfile
        fields = ['student_id', 'department', 'course', 'year_level', 'phone_number', 'is_verified']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BulkUserImportForm(forms.Form):
    """Form for bulk user import with update options"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        help_text="Upload a CSV file with user data"
    )
    
    update_existing = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Update existing users if they already exist (based on username or email)"
    )
    
    overwrite_data = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Overwrite existing user data (name, email, student_id) with CSV data"
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('File must be a CSV file.')
            
            # Check file size (max 5MB)
            if csv_file.size > 5 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 5MB.')
        
        return csv_file


class ElectionManagementForm(forms.ModelForm):
    """Form for election management"""
    
    class Meta:
        model = SchoolElection
        fields = ['title', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CandidateManagementForm(forms.ModelForm):
    """Form for candidate management"""
    
    class Meta:
        model = Candidate
        fields = ['party', 'is_active']
        widgets = {
            'party': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ApplicationReviewForm(forms.ModelForm):
    """Form for reviewing applications"""
    
    class Meta:
        model = CandidateApplication
        fields = ['status', 'review_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SystemSettingsForm(forms.Form):
    """Form for system settings"""
    
    site_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Name of the voting system"
    )
    site_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Description of the voting system"
    )
    allow_registration = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Allow new user registration"
    )
    require_email_verification = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Require email verification for new users"
    )
    max_candidates_per_position = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Maximum number of candidates per position"
    )


class UserSearchForm(forms.Form):
    """Form for searching users"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username, name, or student ID...'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        required=False,
        empty_label="All Courses",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    verification_status = forms.ChoiceField(
        choices=[
            ('', 'All Users'),
            ('verified', 'Verified Only'),
            ('unverified', 'Unverified Only')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CandidateApplicationForm(forms.ModelForm):
    """Form for creating candidate applications (admin-assisted)"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        empty_label="Search and select a user...",
        widget=forms.Select(attrs={
            'class': 'form-control user-autocomplete',
            'data-url': '/admin/users/autocomplete/'
        })
    )
    
    class Meta:
        model = CandidateApplication
        fields = ['user', 'position', 'election', 'party', 'manifesto', 'photo']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
            'election': forms.Select(attrs={'class': 'form-control'}),
            'party': forms.Select(attrs={'class': 'form-control'}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter the candidate\'s manifesto and goals...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get current active election
        from django.utils import timezone
        now = timezone.now()
        current_election = SchoolElection.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).first()
        
        if current_election:
            # Set default election
            self.fields['election'].initial = current_election
            self.fields['election'].queryset = SchoolElection.objects.filter(is_active=True)
            
            # Filter positions for current election
            self.fields['position'].queryset = SchoolPosition.objects.filter(
                elections__election=current_election,
                is_active=True
            ).distinct()
        else:
            # No current election, show all active elections and positions
            self.fields['election'].queryset = SchoolElection.objects.filter(is_active=True)
            self.fields['position'].queryset = SchoolPosition.objects.filter(is_active=True)
        
        # Filter parties
        self.fields['party'].queryset = Party.objects.filter(is_active=True)
        self.fields['party'].empty_label = "No Party (Independent)"
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        position = cleaned_data.get('position')
        election = cleaned_data.get('election')
        
        if user and position and election:
            # Check if user already has an application for this position in this election
            existing_application = CandidateApplication.objects.filter(
                user=user,
                position=position,
                election=election
            ).first()
            
            if existing_application:
                raise ValidationError(
                    f"User {user.get_full_name()} already has an application for {position.name} in {election.title}."
                )
            
            # Check if user already has an application for any position in this election
            existing_election_application = CandidateApplication.objects.filter(
                user=user,
                election=election
            ).exclude(position=position).first()
            
            if existing_election_application:
                raise ValidationError(
                    f"User {user.get_full_name()} already has an application for {existing_election_application.position.name} in {election.title}. "
                    f"A user can only apply for one position per election."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        application = super().save(commit=False)
        application.status = 'pending'  # Set as pending for review
        if commit:
            application.save()
        return application


class ActivityLogSearchForm(forms.Form):
    """Form for searching activity logs"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by description...'
        })
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    action_type = forms.ChoiceField(
        choices=[
            ('', 'All Actions'),
            ('login', 'Login'),
            ('logout', 'Logout'),
            ('vote_submitted', 'Vote Submitted'),
            ('application_submitted', 'Application Submitted'),
            ('user_created', 'User Created'),
            ('election_created', 'Election Created'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
