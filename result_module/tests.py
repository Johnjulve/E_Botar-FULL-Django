from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import ElectionResult, ResultChart, ResultExport, ResultAnalytics, ResultSnapshot
from election_module.models import SchoolElection, SchoolPosition
from candidate_module.models import Candidate, Party
from auth_module.models import UserProfile, Department, Course


class ElectionResultModelTest(TestCase):
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
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
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
    
    def test_election_result_creation(self):
        result = ElectionResult.objects.create(
            election=self.election,
            position=self.position,
            candidate=self.candidate,
            vote_count=100,
            percentage=50.00
        )
        self.assertEqual(str(result), f"{self.candidate.user.username} - {self.position.name} (100 votes)")
        self.assertEqual(result.vote_count, 100)
        self.assertEqual(result.percentage, 50.00)


class ResultChartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
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
    
    def test_result_chart_creation(self):
        chart = ResultChart.objects.create(
            election=self.election,
            position=self.position,
            chart_type='bar',
            title='President Results',
            description='Bar chart showing president election results',
            created_by=self.user
        )
        self.assertEqual(str(chart), f"{chart.title} - {self.election.title}")
        self.assertEqual(chart.chart_type, 'bar')
        self.assertTrue(chart.is_active)


class ResultExportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
        )
    
    def test_result_export_creation(self):
        export = ResultExport.objects.create(
            election=self.election,
            export_format='csv',
            file_path='/path/to/export.csv',
            file_size=1024,
            exported_by=self.user
        )
        # Check that the string representation contains the expected parts
        str_repr = str(export)
        self.assertIn(self.election.title, str_repr)
        self.assertIn('csv', str_repr)
        self.assertEqual(export.export_format, 'csv')
        self.assertEqual(export.file_size, 1024)


class ResultAnalyticsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
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
    
    def test_result_analytics_creation(self):
        analytics = ResultAnalytics.objects.create(
            election=self.election,
            position=self.position,
            metric_name='total_votes',
            metric_value=150.00
        )
        # Check that the string representation contains the expected parts
        str_repr = str(analytics)
        self.assertIn(self.election.title, str_repr)
        self.assertIn('total_votes', str_repr)
        self.assertIn('150', str_repr)
        self.assertEqual(analytics.metric_name, 'total_votes')
        self.assertEqual(analytics.metric_value, 150.00)


class ResultSnapshotModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        self.election = SchoolElection.objects.create(
            title="Test Election",
            start_date=timezone.now(),
            end_date=timezone.now(),
            created_by=self.user
        )
    
    def test_result_snapshot_creation(self):
        snapshot = ResultSnapshot.objects.create(
            election=self.election,
            snapshot_data={'president': {'candidate1': 100, 'candidate2': 50}},
            total_votes=150,
            total_voters=100,
            participation_rate=75.00
        )
        # Check that the string representation contains the expected parts
        str_repr = str(snapshot)
        self.assertIn(self.election.title, str_repr)
        self.assertIn('Snapshot', str_repr)
        self.assertEqual(snapshot.total_votes, 150)
        self.assertEqual(snapshot.total_voters, 100)
        self.assertEqual(snapshot.participation_rate, 75.00)
