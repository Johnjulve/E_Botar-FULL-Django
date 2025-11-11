from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from auth_module.models import UserProfile, Department, Course
from election_management.models import SchoolElection, ElectionPosition, SchoolPosition, Party
from candidates.models import Candidate, CandidateApplication
from votes.models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create a superuser account for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Superuser username')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Superuser email')
        parser.add_argument('--password', type=str, default='admin123', help='Superuser password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
            )
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" created successfully!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Password: {password}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
