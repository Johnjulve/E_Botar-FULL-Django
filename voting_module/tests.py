from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from .models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition
from auth_module.models import UserProfile, Department, Course


class SchoolVoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.department = Department.objects.create(
            name="Computer Science",
            code="CS"
        )
        self.course = Course.objects.create(
            department=self.department,
            name="Software Engineering",
            code="SE101"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            student_id="2024001",
            department=self.department,
            course=self.course,
            year_level="3rd Year",
            is_verified=True
        )
        
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.user
        )
        
        self.position = SchoolPosition.objects.create(
            name="President",
            description="Student body president"
        )
        
        self.candidate = Candidate.objects.create(
            user=self.user,
            party=None
        )
        
        self.application = CandidateApplication.objects.create(
            candidate=self.candidate,
            position=self.position,
            status='approved'
        )
    
    def test_vote_creation(self):
        vote = SchoolVote.objects.create(
            voter=self.user,
            candidate=self.candidate,
            position=self.position,
            election=self.election
        )
        self.assertEqual(str(vote), f"{self.user.username} voted for {self.candidate.user.username} for {self.position.name}")
        self.assertTrue(vote.receipt_code)
        self.assertEqual(len(vote.receipt_code), 8)


class VoteReceiptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.user
        )
    
    def test_receipt_creation(self):
        receipt = VoteReceipt.objects.create(
            voter=self.user,
            election=self.election,
            receipt_code="ABC12345"
        )
        self.assertEqual(str(receipt), f"Receipt ABC12345 for {self.election.title}")
        self.assertTrue(receipt.encrypted_receipt_code)


class AnonVoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.user
        )
        self.position = SchoolPosition.objects.create(
            name="President",
            description="Student body president"
        )
        self.candidate = Candidate.objects.create(
            user=self.user,
            party=None
        )
    
    def test_anon_vote_creation(self):
        anon_vote = AnonVote.objects.create(
            candidate=self.candidate,
            position=self.position,
            election=self.election
        )
        self.assertEqual(str(anon_vote), f"Anonymous vote for {self.candidate.user.username} for {self.position.name}")


class EncryptedBallotModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.user
        )
    
    def test_encrypted_ballot_creation(self):
        ballot = EncryptedBallot.objects.create(
            election=self.election,
            encrypted_data="encrypted_vote_data_here"
        )
        self.assertEqual(str(ballot), f"Encrypted ballot for {self.election.title}")
        self.assertEqual(ballot.encrypted_data, "encrypted_vote_data_here")
