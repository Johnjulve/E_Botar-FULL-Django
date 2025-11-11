from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from auth_module.models import UserProfile, Department, Course
from election_module.models import SchoolElection, ElectionPosition, SchoolPosition, Party
from candidate_module.models import Candidate, CandidateApplication
from voting_module.models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from django.utils import timezone


class Command(BaseCommand):
    help = 'Reset database while keeping academic structure (departments and courses)'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm database reset')
        parser.add_argument('--keep-superusers', action='store_true', help='Keep superuser accounts')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will reset the database while keeping academic structure!\n'
                    'Use --confirm flag to proceed.\n'
                    'Use --keep-superusers to preserve superuser accounts.'
                )
            )
            return

        self.stdout.write('Resetting database (keeping academic structure)...')
        
        with transaction.atomic():
            # Clear votes and related data
            self.stdout.write('Clearing votes and receipts...')
            SchoolVote.objects.all().delete()
            VoteReceipt.objects.all().delete()
            AnonVote.objects.all().delete()
            EncryptedBallot.objects.all().delete()
            
            # Clear candidates
            self.stdout.write('Clearing candidates...')
            Candidate.objects.all().delete()
            CandidateApplication.objects.all().delete()
            
            # Clear elections
            self.stdout.write('Clearing elections...')
            SchoolElection.objects.all().delete()
            ElectionPosition.objects.all().delete()
            SchoolPosition.objects.all().delete()
            Party.objects.all().delete()
            
            # Clear users (optionally keep superusers)
            if options['keep_superusers']:
                self.stdout.write('Clearing non-superuser accounts...')
                User.objects.filter(is_superuser=False).delete()
            else:
                self.stdout.write('Clearing all user accounts...')
                User.objects.all().delete()
            
            UserProfile.objects.all().delete()
            
            # Keep departments and courses - they are preserved
        
        self.stdout.write(
            self.style.SUCCESS('Database reset successfully! Academic structure preserved.')
        )
