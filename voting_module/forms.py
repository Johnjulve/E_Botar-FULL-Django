from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import SchoolVote, VoteReceipt
from election_module.models import SchoolElection, SchoolPosition
from candidate_module.models import Candidate


class VoteForm(forms.Form):
    """Form for submitting votes"""
    
    def __init__(self, election=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if election:
            # Create a field for each position in the election
            for election_position in election.positions.all().order_by('order'):
                position = election_position.position  # Get the actual SchoolPosition
                candidates = Candidate.objects.filter(
                    applications__position=position,
                    applications__election=election,
                    applications__status='approved'
                ).distinct()
                
                self.fields[f'position_{position.id}'] = forms.ModelChoiceField(
                    queryset=candidates,
                    empty_label="Select a candidate",
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                    label=position.name,
                    required=True
                )
    
    def clean(self):
        cleaned_data = super().clean()
        # Additional validation can be added here
        return cleaned_data


class VoteReceiptForm(forms.Form):
    """Form for verifying vote receipts"""
    
    receipt_code = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter receipt code',
            'pattern': '[A-Z0-9]{8}',
            'title': 'Receipt code should be 8 characters (letters and numbers)'
        }),
        help_text="Enter your 8-character receipt code"
    )
    
    def clean_receipt_code(self):
        receipt_code = self.cleaned_data.get('receipt_code')
        if receipt_code:
            receipt_code = receipt_code.upper().strip()
            if len(receipt_code) != 8:
                raise ValidationError('Receipt code must be exactly 8 characters.')
            if not receipt_code.isalnum():
                raise ValidationError('Receipt code can only contain letters and numbers.')
        return receipt_code


class VotingSearchForm(forms.Form):
    """Form for searching votes and receipts"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by election, candidate, or receipt...'
        })
    )
    election = forms.ModelChoiceField(
        queryset=SchoolElection.objects.filter(is_active=True),
        required=False,
        empty_label="All Elections",
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


class VoteConfirmationForm(forms.Form):
    """Form for confirming votes before submission"""
    
    confirm_votes = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="I confirm that my votes are correct and I want to submit them"
    )
    
    def clean_confirm_votes(self):
        confirm = self.cleaned_data.get('confirm_votes')
        if not confirm:
            raise ValidationError('You must confirm your votes before submitting.')
        return confirm
