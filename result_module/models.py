from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from election_module.models import SchoolElection, SchoolPosition
from candidate_module.models import Candidate


class ElectionResult(models.Model):
    """Model for storing election results"""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['election', 'position', 'candidate']
        ordering = ['-vote_count']
        verbose_name = 'Election Result'
        verbose_name_plural = 'Election Results'
    
    def __str__(self):
        return f"{self.candidate.user.username} - {self.position.name} ({self.vote_count} votes)"


class ResultChart(models.Model):
    """Model for storing chart configurations"""
    CHART_TYPE_CHOICES = [
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('line', 'Line Chart'),
        ('doughnut', 'Doughnut Chart'),
    ]
    
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, null=True, blank=True)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Result Chart'
        verbose_name_plural = 'Result Charts'
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"


class ResultExport(models.Model):
    """Model for tracking result exports"""
    EXPORT_FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMAT_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField()
    exported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    exported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-exported_at']
        verbose_name = 'Result Export'
        verbose_name_plural = 'Result Exports'
    
    def __str__(self):
        return f"{self.election.title} - {self.export_format} ({self.exported_at})"


class ResultAnalytics(models.Model):
    """Model for storing result analytics"""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, null=True, blank=True)
    metric_name = models.CharField(max_length=100)
    metric_value = models.DecimalField(max_digits=10, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Result Analytics'
        verbose_name_plural = 'Result Analytics'
    
    def __str__(self):
        return f"{self.election.title} - {self.metric_name}: {self.metric_value}"


class ResultSnapshot(models.Model):
    """Model for storing result snapshots"""
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    snapshot_data = models.JSONField()
    total_votes = models.PositiveIntegerField()
    total_voters = models.PositiveIntegerField()
    participation_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Result Snapshot'
        verbose_name_plural = 'Result Snapshots'
    
    def __str__(self):
        return f"{self.election.title} - Snapshot ({self.created_at})"
