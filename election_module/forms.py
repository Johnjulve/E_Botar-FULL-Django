from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import SchoolElection, SchoolPosition, Party


class ElectionForm(forms.ModelForm):
    """Form for creating and editing elections"""
    
    class Meta:
        model = SchoolElection
        fields = ['start_year', 'end_year', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2025 for SY 2025-2026',
                'min': 2023,
                'max': 2030
            }),
            'end_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2026 for SY 2025-2026',
                'min': 2023,
                'max': 2030
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate year fields
        if start_year and end_year:
            if end_year != start_year + 1:
                raise ValidationError('End year must be exactly one year after start year (e.g., 2025-2026).')
            
            if start_year < 2020 or start_year > 2030:
                raise ValidationError('Start year must be between 2020 and 2030.')
            
            if end_year < 2021 or end_year > 2031:
                raise ValidationError('End year must be between 2021 and 2031.')
        
        # Validate date fields
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError('End date must be after start date.')
            
            if start_date < timezone.now().replace(hour=0, minute=0, second=0, microsecond=0):
                raise ValidationError('Start date must be today or in the future.')
            
            # Check if election duration is reasonable (not more than 30 days)
            duration = end_date - start_date
            if duration > timedelta(days=30):
                raise ValidationError('Election duration cannot exceed 30 days.')
        
        return cleaned_data


class PositionForm(forms.ModelForm):
    """Form for creating and editing positions"""
    
    class Meta:
        model = SchoolPosition
        fields = ['name', 'position_type', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter position name'
            }),
            'position_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter position description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class PartyForm(forms.ModelForm):
    """Form for creating and editing parties"""
    
    class Meta:
        model = Party
        fields = ['name', 'description', 'logo', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter party name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter party description'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color and not color.startswith('#'):
            color = '#' + color
        return color


class ElectionPositionForm(forms.Form):
    """Form for adding positions to elections"""
    
    position = forms.ModelChoiceField(
        queryset=SchoolPosition.objects.filter(is_active=True),
        empty_label="Select a position",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    order = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1
        })
    )
    
    def __init__(self, election=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if election:
            # Exclude positions already in the election
            existing_positions = election.positions.values_list('id', flat=True)
            self.fields['position'].queryset = SchoolPosition.objects.filter(
                is_active=True
            ).exclude(id__in=existing_positions)


class ElectionSearchForm(forms.Form):
    """Form for searching elections"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search elections...'
        })
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('upcoming', 'Upcoming'),
            ('completed', 'Completed')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
