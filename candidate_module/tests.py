from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party
from auth_module.models import UserProfile, Department, Course


class CandidateModelTest(TestCase):
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
        self.party = Party.objects.create(
            name="Test Party",
            description="Test party description"
        )
    
    def test_candidate_creation(self):
        candidate = Candidate.objects.create(
            user=self.user,
            party=self.party
        )
        self.assertEqual(str(candidate), f"{self.user.username} - {self.party.name}")
        self.assertTrue(candidate.is_active)
    
    def test_candidate_without_party(self):
        candidate = Candidate.objects.create(
            user=self.user,
            party=None
        )
        self.assertEqual(str(candidate), f"{self.user.username} - Independent")
        self.assertTrue(candidate.is_active)


class CandidateApplicationModelTest(TestCase):
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
        self.party = Party.objects.create(
            name="Test Party",
            description="Test party description"
        )
        self.candidate = Candidate.objects.create(
            user=self.user,
            party=self.party
        )
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
    
    def test_application_creation(self):
        application = CandidateApplication.objects.create(
            candidate=self.candidate,
            position=self.position,
            motivation="I want to serve the student body",
            qualifications="Leadership experience"
        )
        self.assertEqual(str(application), f"{self.candidate.user.username} - {self.position.name}")
        self.assertEqual(application.status, 'pending')
    
    def test_application_approval(self):
        application = CandidateApplication.objects.create(
            candidate=self.candidate,
            position=self.position,
            motivation="I want to serve the student body",
            qualifications="Leadership experience"
        )
        self.assertEqual(application.status, 'pending')
        
        application.status = 'approved'
        application.save()
        
        self.assertEqual(application.status, 'approved')
    
    def test_application_rejection(self):
        application = CandidateApplication.objects.create(
            candidate=self.candidate,
            position=self.position,
            motivation="I want to serve the student body",
            qualifications="Leadership experience"
        )
        self.assertEqual(application.status, 'pending')
        
        application.status = 'rejected'
        application.save()
        
        self.assertEqual(application.status, 'rejected')
