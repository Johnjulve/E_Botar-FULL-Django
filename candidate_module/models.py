from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from election_module.models import SchoolPosition, SchoolElection, Party, ElectionPosition


class Candidate(models.Model):
    """Model for candidates running for school positions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidates')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='candidates', null=True, blank=True)
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='candidates')
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    manifesto = models.TextField(help_text="Campaign manifesto and goals")
    photo = models.ImageField(upload_to='candidate_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add reference to the approved application
    approved_application = models.OneToOneField('CandidateApplication', on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position.name}"
    
    def clean(self):
        """Validate that candidate was created through proper application process"""
        # Check if there's an approved application for this user/position/election
        if not self.approved_application:
            approved_app = CandidateApplication.objects.filter(
                user=self.user,
                position=self.position,
                election=self.election,
                status='approved'
            ).first()
            
            if not approved_app:
                raise ValidationError(
                    f"Candidate {self.user.get_full_name()} cannot be created without an approved application for {self.position.name}."
                )
            else:
                # Link the approved application
                self.approved_application = approved_app
    
    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    def vote_count(self):
        """Get the vote count for this candidate"""
        try:
            from voting_module.models import AnonVote
            return AnonVote.objects.filter(candidate=self, election=self.election).count()
        except Exception as e:
            print(f"Error getting vote count for candidate {self.user.get_full_name()}: {str(e)}")
            return 0
    
    def percentage(self):
        """Calculate vote percentage for this candidate"""
        try:
            from voting_module.models import AnonVote
            total_votes = AnonVote.objects.filter(election=self.election, position=self.position).count()
            if total_votes == 0:
                return 0
            return round((self.vote_count() / total_votes) * 100, 1)
        except Exception:
            return 0
    
    class Meta:
        ordering = ['position', 'user__first_name']
        unique_together = ['user', 'election', 'position']


class CandidateApplication(models.Model):
    """Model for student candidate applications"""
    APPLICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_applications')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='applications')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='applications')
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    manifesto = models.TextField(help_text="Your campaign manifesto and goals")
    photo = models.ImageField(upload_to='candidate_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position.name} ({self.get_status_display()})"
    
    def clean(self):
        """Validate application rules"""
        
        # Rule 1: Check if same party already has a candidate for this position in this election
        if self.party:
            existing_candidate = Candidate.objects.filter(
                position=self.position,
                election=self.election,
                party=self.party,
                is_active=True
            ).exclude(user=self.user).first()
            
            if existing_candidate:
                raise ValidationError(
                    f"Party '{self.party.name}' already has a candidate ({existing_candidate.user.get_full_name()}) "
                    f"for the position '{self.position.name}' in this election."
                )
        
        # Rule 2: Check if user ran for the same position in the previous election
        if self.election and self.position:
            # Get the previous election (assuming elections are yearly)
            previous_election = SchoolElection.objects.filter(
                start_date__lt=self.election.start_date
            ).order_by('-start_date').first()
            
            if previous_election:
                # Check if user was a candidate for the same position in the previous election
                previous_candidate = Candidate.objects.filter(
                    user=self.user,
                    position=self.position,
                    election=previous_election,
                    is_active=True
                ).first()
                
                if previous_candidate:
                    raise ValidationError(
                        f"You cannot run for the same position '{self.position.name}' "
                        f"in consecutive elections. You previously ran in {previous_election.title}."
                    )
    
    class Meta:
        unique_together = ['user', 'position', 'election']
        ordering = ['-submitted_at']
        verbose_name = 'Candidate Application'
        verbose_name_plural = 'Candidate Applications'
