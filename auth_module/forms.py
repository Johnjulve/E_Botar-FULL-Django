from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Department, Course, UserProfile
import secrets
import string


class BulkUserUploadForm(forms.Form):
    file = forms.FileField(
        help_text=(
            "Upload .xlsx or .csv with columns: username, email, first_name, last_name"
        )
    )
    # Password reset options removed; resets are handled in Admin UI only.

    def clean(self):
        cleaned = super().clean()
        uploaded = cleaned.get("file")
        if uploaded:
            lower_name = uploaded.name.lower()
            if not (lower_name.endswith(".xlsx") or lower_name.endswith(".csv")):
                raise forms.ValidationError("File must be .xlsx or .csv")
        return cleaned


class CreateUserForm(forms.ModelForm):
    """Form for creating new users with auto-generated password"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False,
        help_text="Password will be auto-generated"
    )
    confirm_admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Admin Password",
        help_text="Enter your admin password to create this user"
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.admin_user = kwargs.pop('admin_user', None)
        super().__init__(*args, **kwargs)
        
        # Generate a random password
        if not self.instance.pk:  # Only for new users
            self.generated_password = self.generate_password()
            self.fields['password'].initial = self.generated_password
    
    def generate_password(self):
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(8))
        return password
    
    def clean_confirm_admin_password(self):
        admin_password = self.cleaned_data.get('confirm_admin_password')
        if not admin_password:
            raise forms.ValidationError("Admin password is required to create users.")
        
        if not self.admin_user or not self.admin_user.check_password(admin_password):
            raise forms.ValidationError("Invalid admin password.")
        
        return admin_password
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.pk:  # New user
            user.set_password(self.generated_password)
        if commit:
            user.save()
        return user


class PasswordVerificationForm(forms.Form):
    """Form for verifying admin password to show generated password"""
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Admin Password",
        help_text="Enter your admin password to view the generated password"
    )
    
    def __init__(self, *args, **kwargs):
        self.admin_user = kwargs.pop('admin_user', None)
        super().__init__(*args, **kwargs)
    
    def clean_admin_password(self):
        admin_password = self.cleaned_data.get('admin_password')
        if not admin_password:
            raise forms.ValidationError("Admin password is required.")
        
        if not self.admin_user or not self.admin_user.check_password(admin_password):
            raise forms.ValidationError("Invalid admin password.")
        
        return admin_password


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['student_id', 'department', 'course', 'year_level', 'phone_number', 'avatar']
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXX-XXXXX (e.g., 2024-12345)',
                'pattern': r'\d{4}-\d{5}',
                'title': 'Student ID must be in format XXXX-XXXXX (e.g., 2024-12345)'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'year_level': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id:
            import re
            if not re.match(r'^\d{4}-\d{5}$', student_id):
                raise forms.ValidationError('Student ID must be in format(e.g., 2024-12345)')
        return student_id

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['department', 'name', 'code', 'description', 'is_active']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
