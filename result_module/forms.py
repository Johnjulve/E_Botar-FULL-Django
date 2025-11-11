from django import forms
from django.core.exceptions import ValidationError

from .models import ElectionResult, ResultChart, ResultExport, ResultAnalytics


class ResultFilterForm(forms.Form):
    """Form for filtering results"""
    
    election = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Elections",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    position = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Positions",
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
    
    def __init__(self, *args, **kwargs):
        elections = kwargs.pop('elections', None)
        positions = kwargs.pop('positions', None)
        super().__init__(*args, **kwargs)
        
        if elections:
            self.fields['election'].queryset = elections
        if positions:
            self.fields['position'].queryset = positions


class ChartConfigForm(forms.ModelForm):
    """Form for configuring charts"""
    
    class Meta:
        model = ResultChart
        fields = ['position', 'chart_type', 'title', 'description', 'config']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
            'chart_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'config': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def clean_config(self):
        config = self.cleaned_data.get('config')
        if config:
            try:
                import json
                json.loads(config)
            except json.JSONDecodeError:
                raise ValidationError('Config must be valid JSON.')
        return config


class ResultExportForm(forms.Form):
    """Form for exporting results"""
    
    EXPORT_FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    include_charts = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Include charts in export"
    )
    include_statistics = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Include statistics in export"
    )


class ResultComparisonForm(forms.Form):
    """Form for comparing results between elections"""
    
    elections = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select elections to compare"
    )
    comparison_type = forms.ChoiceField(
        choices=[
            ('vote_counts', 'Vote Counts'),
            ('percentages', 'Percentages'),
            ('participation', 'Participation Rates'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        elections_queryset = kwargs.pop('elections_queryset', None)
        super().__init__(*args, **kwargs)
        
        if elections_queryset:
            self.fields['elections'].queryset = elections_queryset


class AnalyticsForm(forms.Form):
    """Form for configuring analytics"""
    
    metric_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Name of the metric to calculate"
    )
    calculation_method = forms.ChoiceField(
        choices=[
            ('sum', 'Sum'),
            ('average', 'Average'),
            ('count', 'Count'),
            ('percentage', 'Percentage'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    group_by = forms.ChoiceField(
        choices=[
            ('position', 'Position'),
            ('candidate', 'Candidate'),
            ('department', 'Department'),
            ('course', 'Course'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
