from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from candidate_module.models import Candidate
from election_module.models import SchoolPosition, SchoolElection


class SchoolVote(models.Model):
    """Model for votes in school elections"""
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE)
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE)
    receipt_code = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    encrypted_receipt_code = models.TextField(blank=True, null=True, help_text="Encrypted receipt code for security")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['voter', 'position', 'election']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Override save to automatically encrypt receipt code"""
        if self.receipt_code and not self.encrypted_receipt_code:
            from E_Botar.services.security import encrypt_string
            self.encrypted_receipt_code = encrypt_string(self.receipt_code)
        super().save(*args, **kwargs)
    
    def get_decrypted_receipt(self):
        """Decrypt and return the receipt code"""
        if self.encrypted_receipt_code:
            from E_Botar.services.security import decrypt_string
            return decrypt_string(self.encrypted_receipt_code)
        return self.receipt_code  # Fallback to plaintext if not encrypted
    
    def get_anonymized_receipt(self):
        """Get anonymized receipt for display"""
        from E_Botar.services.security import generate_anonymous_receipt
        receipt = self.get_decrypted_receipt()
        if receipt:
            return generate_anonymous_receipt(receipt)
        return None
    
    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.user.get_full_name()} as {self.position.name}"


class VoteReceipt(models.Model):
    """Minimal record proving a user has voted in an election.

    This model stores only the essential information needed to verify that a user
    has voted, without storing the actual vote choices. This provides privacy
    while maintaining auditability.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_receipts')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='receipts')
    receipt_code = models.CharField(max_length=32, unique=True, db_index=True)
    encrypted_receipt_code = models.TextField(help_text="Encrypted receipt code for security")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'election']
        ordering = ['-created_at']
    
    def get_decrypted_receipt(self):
        """Decrypt and return the receipt code"""
        from E_Botar.services.security import decrypt_string
        return decrypt_string(self.encrypted_receipt_code)
    
    def get_anonymized_receipt(self):
        """Get anonymized receipt for display"""
        from E_Botar.services.security import generate_anonymous_receipt
        receipt = self.get_decrypted_receipt()
        if receipt:
            return generate_anonymous_receipt(receipt)
        return None
    
    def __str__(self):
        return f"Receipt {self.receipt_code[:8]}... for {self.user.username}"


class AnonVote(models.Model):
    """Anonymized vote record for tallying results.

    This model stores vote choices without linking them to specific users,
    enabling privacy-preserving vote counting and result generation.
    """
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='anon_votes')
    position = models.ForeignKey(SchoolPosition, on_delete=models.CASCADE, related_name='anon_votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='anon_votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Vote for {self.candidate.user.get_full_name()} in {self.position.name}"


class EncryptedBallot(models.Model):
    """Encrypted ballot copy for personal verification.

    This model stores an encrypted copy of the user's ballot choices,
    allowing users to verify their votes while maintaining privacy.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='encrypted_ballots')
    election = models.ForeignKey(SchoolElection, on_delete=models.CASCADE, related_name='encrypted_ballots')
    encrypted_data = models.TextField(help_text="Encrypted ballot data")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'election']
        ordering = ['-created_at']
    
    def get_decrypted_ballot(self):
        """Decrypt and return the ballot data"""
        from E_Botar.services.security import decrypt_vote_data
        return decrypt_vote_data(self.encrypted_data)
    
    def __str__(self):
        return f"Encrypted ballot for {self.user.username} in {self.election.title}"
