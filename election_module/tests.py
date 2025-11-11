from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from .models import SchoolElection, SchoolPosition, ElectionPosition, Party


class SchoolElectionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
    
    def test_election_creation(self):
        election = SchoolElection.objects.create(
            title="Test Election",
            description="Test election description",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            created_by=self.user
        )
        self.assertEqual(str(election), "Test Election")
        self.assertTrue(election.is_active)
        self.assertEqual(election.created_by, self.user)
    
    def test_election_is_active_now(self):
        # Active election
        active_election = SchoolElection.objects.create(
            title="Active Election",
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=1),
            created_by=self.user
        )
        self.assertTrue(active_election.is_active_now())
        
        # Inactive election
        inactive_election = SchoolElection.objects.create(
            title="Inactive Election",
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=2),
            created_by=self.user
        )
        self.assertFalse(inactive_election.is_active_now())


class SchoolPositionModelTest(TestCase):
    def test_position_creation(self):
        position = SchoolPosition.objects.create(
            name="President",
            description="Student body president",
            max_candidates=2
        )
        self.assertEqual(str(position), "President")
        self.assertTrue(position.is_active)
        self.assertEqual(position.max_candidates, 2)


class PartyModelTest(TestCase):
    def test_party_creation(self):
        party = Party.objects.create(
            name="Test Party",
            description="Test party description",
            color="#FF0000"
        )
        self.assertEqual(str(party), "Test Party")
        self.assertTrue(party.is_active)
        self.assertEqual(party.color, "#FF0000")


class ElectionPositionModelTest(TestCase):
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
    
    def test_election_position_creation(self):
        election_position = ElectionPosition.objects.create(
            election=self.election,
            position=self.position,
            order=1
        )
        self.assertEqual(str(election_position), "Test Election - President")
        self.assertEqual(election_position.order, 1)
