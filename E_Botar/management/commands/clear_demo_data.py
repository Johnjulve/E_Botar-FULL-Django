from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from auth_module.models import UserProfile, Department, Course
from election_module.models import SchoolElection, ElectionPosition, SchoolPosition, Party
from candidate_module.models import Candidate, CandidateApplication
from voting_module.models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot


class Command(BaseCommand):
    help = 'Clear all demo data from the database'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm that you want to clear all data')
        parser.add_argument('--keep-superusers', action='store_true', help='Keep superuser accounts')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will clear ALL demo data from the database!\n'
                    'Use --confirm flag to proceed.\n'
                    'Use --keep-superusers to preserve superuser accounts.'
                )
            )
            return

        self.stdout.write('Clearing demo data...')
        
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
            
            # Clear academic structure (optional)
            self.stdout.write('Clearing academic structure...')
            Course.objects.all().delete()
            Department.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS('Demo data cleared successfully!')
        )
