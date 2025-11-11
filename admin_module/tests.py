from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from auth_module.models import UserProfile, Department, Course, ActivityLog
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party
from voting_module.models import SchoolVote, VoteReceipt


class AdminModuleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        self.user.is_staff = True
        self.user.save()
        
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


class UserManagementTestCase(AdminModuleTestCase):
    def test_user_creation(self):
        """Test user creation functionality"""
        new_user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )
        
        UserProfile.objects.create(
            user=new_user,
            student_id="2024002",
            department=self.department,
            course=self.course,
            year_level="2nd Year"
        )
        
        self.assertEqual(UserProfile.objects.count(), 2)
        self.assertEqual(new_user.username, "newuser")
    
    def test_user_verification(self):
        """Test user verification functionality"""
        # Create a new user profile that is not verified initially
        new_user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        
        new_profile = UserProfile.objects.create(
            user=new_user,
            student_id="2024003",
            department=self.department,
            course=self.course,
            year_level="2nd Year",
            is_verified=False  # Explicitly set to False
        )
        
        self.assertFalse(new_profile.is_verified)
        
        new_profile.is_verified = True
        new_profile.save()
        
        self.assertTrue(new_profile.is_verified)


class ElectionManagementTestCase(AdminModuleTestCase):
    def setUp(self):
        super().setUp()
        self.election = SchoolElection.objects.create(
            title="Test Election",
            description="Test election description",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
        )
    
    def test_election_creation(self):
        """Test election creation functionality"""
        self.assertEqual(SchoolElection.objects.count(), 1)
        self.assertEqual(self.election.title, "Test Election")
    
    def test_election_status(self):
        """Test election status functionality"""
        self.assertTrue(self.election.is_active)
        
        self.election.is_active = False
        self.election.save()
        
        self.assertFalse(self.election.is_active)


class CandidateManagementTestCase(AdminModuleTestCase):
    def setUp(self):
        super().setUp()
        self.election = SchoolElection.objects.create(
            title="Test Election",
            description="Test election description",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
        )
        
        self.party = Party.objects.create(
            name="Test Party",
            description="Test party description"
        )
        
        self.candidate = Candidate.objects.create(
            user=self.user,
            party=self.party,
            election=self.election
        )
        
        self.position = SchoolPosition.objects.create(
            name="President",
            description="Student body president"
        )
        
        self.application = CandidateApplication.objects.create(
            user=self.user,
            position=self.position,
            election=self.election,
            status='pending'
        )
    
    def test_candidate_creation(self):
        """Test candidate creation functionality"""
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(self.candidate.user, self.user)
        self.assertEqual(self.candidate.party, self.party)
    
    def test_application_approval(self):
        """Test application approval functionality"""
        self.assertEqual(self.application.status, 'pending')
        
        self.application.status = 'approved'
        self.application.save()
        
        self.assertEqual(self.application.status, 'approved')
    
    def test_application_rejection(self):
        """Test application rejection functionality"""
        self.assertEqual(self.application.status, 'pending')
        
        self.application.status = 'rejected'
        self.application.save()
        
        self.assertEqual(self.application.status, 'rejected')


class VotingManagementTestCase(AdminModuleTestCase):
    def setUp(self):
        super().setUp()
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
        )
        
        self.position = SchoolPosition.objects.create(
            name="President",
            description="Student body president"
        )
        
        self.party = Party.objects.create(
            name="Test Party",
            description="Test party description"
        )
        
        self.candidate = Candidate.objects.create(
            user=self.user,
            party=self.party,
            election=self.election
        )
    
    def test_vote_creation(self):
        """Test vote creation functionality"""
        vote = SchoolVote.objects.create(
            voter=self.user,
            candidate=self.candidate,
            position=self.position,
            election=self.election
        )
        
        self.assertEqual(SchoolVote.objects.count(), 1)
        self.assertEqual(vote.voter, self.user)
        self.assertEqual(vote.candidate, self.candidate)
    
    def test_receipt_creation(self):
        """Test receipt creation functionality"""
        receipt = VoteReceipt.objects.create(
            user=self.user,
            election=self.election,
            receipt_code="ABC12345"
        )
        
        self.assertEqual(VoteReceipt.objects.count(), 1)
        self.assertEqual(receipt.user, self.user)
        self.assertEqual(receipt.election, self.election)


class ActivityLogTestCase(AdminModuleTestCase):
    def test_activity_log_creation(self):
        """Test activity log creation functionality"""
        initial_count = ActivityLog.objects.count()
        
        log = ActivityLog.objects.create(
            user=self.user,
            action_type='test_action',
            description='Test activity log',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(ActivityLog.objects.count(), initial_count + 1)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action_type, 'test_action')
    
    def test_activity_log_without_user(self):
        """Test activity log creation without user"""
        initial_count = ActivityLog.objects.count()
        
        log = ActivityLog.objects.create(
            user=None,
            action_type='system_action',
            description='System activity log',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(ActivityLog.objects.count(), initial_count + 1)
        self.assertIsNone(log.user)
        self.assertEqual(log.action_type, 'system_action')
