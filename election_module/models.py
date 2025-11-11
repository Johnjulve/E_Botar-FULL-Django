from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Party(models.Model):
    """Model for political parties"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='party_logos/', blank=True, null=True)
    color = models.CharField(max_length=7, default='#0b6e3b', help_text="Hex color code for party branding")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Party'
        verbose_name_plural = 'Parties'


class SchoolPosition(models.Model):
    """Model for school administration positions"""
    POSITION_TYPES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('auditor', 'Auditor'),
        ('public_info', 'Public Information Officer'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    position_type = models.CharField(max_length=20, choices=POSITION_TYPES, default='other')
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def total_votes(self):
        """Calculate total votes for all candidates in this position"""
        try:
            from voting_module.models import AnonVote
            return AnonVote.objects.filter(position=self).count()
        except Exception as e:
            print(f"Error calculating total votes for position {self.name}: {str(e)}")
            return 0
    
    class Meta:
        ordering = ['display_order', 'position_type', 'name']


class SchoolElection(models.Model):
    """Model for school election periods"""
    title = models.CharField(max_length=200)
    start_year = models.IntegerField(null=True, blank=True, help_text="Start year for SY format (e.g., 2025 for SY 2025-2026)")
    end_year = models.IntegerField(null=True, blank=True, help_text="End year for SY format (e.g., 2026 for SY 2025-2026)")
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Compatibility: some tests/admin expect a creator field
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Always auto-generate title from years
        if self.start_year and self.end_year:
            self.title = f"SY {self.start_year}-{self.end_year}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def is_active_now(self):
        now = timezone.now()
        # Election is considered active only if within schedule and marked active
        return self.is_active and (self.start_date <= now <= self.end_date)
    
    def total_votes(self):
        """Return the number of receipts issued (one per voter) for this election.
        Uses privacy-preserving receipts instead of legacy user-linked votes.
        """
        from voting_module.models import VoteReceipt
        return VoteReceipt.objects.filter(election=self).count()
    
    class Meta:
        ordering = ['-start_date']


class ElectionPosition(models.Model):
    """Model to link elections with positions"""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='positions')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='elections')
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    def __str__(self):
        return f"{self.election.title} - {self.position.name}"
    
    class Meta:
        unique_together = ['election', 'position']
        ordering = ['order']
