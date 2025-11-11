from django import forms
from django.core.exceptions import ValidationError
from .models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['user', 'position', 'election', 'party', 'manifesto', 'photo', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'election': forms.Select(attrs={'class': 'form-select'}),
            'party': forms.Select(attrs={'class': 'form-select'}),
            'manifesto': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Campaign manifesto and goals'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['election'].queryset = SchoolElection.objects.filter(is_active=True)
        self.fields['party'].queryset = Party.objects.filter(is_active=True)
        self.fields['election'].empty_label = "Select an election"
        self.fields['party'].empty_label = "Select a registered party (optional)"


class CandidateApplicationForm(forms.ModelForm):
    class Meta:
        model = CandidateApplication
        fields = ['position', 'election', 'party', 'manifesto', 'photo']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-select'}),
            'election': forms.Select(attrs={'class': 'form-select'}),
            'party': forms.Select(attrs={'class': 'form-select'}),
            'manifesto': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Describe your platform, goals, and why you should be elected...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show upcoming elections and positions
        self.fields['election'].queryset = SchoolElection.objects.filter(is_active=True)
        self.fields['position'].queryset = SchoolPosition.objects.filter(is_active=True)
        self.fields['party'].queryset = Party.objects.filter(is_active=True)
        
        # Add empty option for party selection
        self.fields['party'].empty_label = "Select a registered party (optional)"
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Populate instance with cleaned data for validation
        for field_name, value in cleaned_data.items():
            setattr(self.instance, field_name, value)
        
        # Call the model's clean method for additional validation
        if hasattr(self.instance, 'clean'):
            try:
                self.instance.clean()
            except ValidationError as e:
                # Convert ValidationError to form validation error
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        self.add_error(field, errors)
                elif hasattr(e, 'messages'):
                    for message in e.messages:
                        self.add_error(None, message)
                else:
                    self.add_error(None, str(e))
            except Exception as e:
                self.add_error(None, str(e))
        
        return cleaned_data
