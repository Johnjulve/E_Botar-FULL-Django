from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from auth_module.models import UserProfile, Department, Course
from election_module.models import SchoolElection, ElectionPosition, SchoolPosition, Party
from candidate_module.models import Candidate, CandidateApplication
from voting_module.models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from django.utils import timezone


class Command(BaseCommand):
    help = 'Debug election results and vote counting'

    def add_arguments(self, parser):
        parser.add_argument('--election-id', type=int, help='Specific election ID to debug')
        parser.add_argument('--position-id', type=int, help='Specific position ID to debug')
        parser.add_argument('--verbose', action='store_true', help='Show detailed vote information')

    def handle(self, *args, **options):
        self.stdout.write('Election Results Debug Report')
        self.stdout.write('=' * 50)
        
        # Get elections to debug
        if options['election_id']:
            elections = SchoolElection.objects.filter(id=options['election_id'])
        else:
            elections = SchoolElection.objects.all()
        
        for election in elections:
            self.stdout.write(f'\nElection: {election.title}')
            self.stdout.write(f'Status: {"Active" if election.is_active else "Inactive"}')
            self.stdout.write(f'Period: {election.start_date} to {election.end_date}')
            self.stdout.write('-' * 30)
            
            # Get positions for this election
            if options['position_id']:
                positions = ElectionPosition.objects.filter(
                    election=election,
                    position_id=options['position_id']
                )
            else:
                positions = election.positions.all()
            
            for election_position in positions:
                position = election_position.position
                self.stdout.write(f'\nPosition: {position.name}')
                
                # Get candidates for this position
                candidates = Candidate.objects.filter(
                    election=election,
                    position=position
                )
                
                if not candidates.exists():
                    self.stdout.write('  No candidates found.')
                    continue
                
                # Count votes for each candidate
                total_votes = 0
                candidate_votes = {}
                
                for candidate in candidates:
                    vote_count = AnonVote.objects.filter(
                        election=election,
                        position=position,
                        candidate=candidate
                    ).count()
                    
                    candidate_votes[candidate] = vote_count
                    total_votes += vote_count
                
                # Display results
                self.stdout.write(f'  Total Votes: {total_votes}')
                
                if total_votes > 0:
                    for candidate, votes in sorted(candidate_votes.items(), key=lambda x: x[1], reverse=True):
                        percentage = (votes / total_votes) * 100
                        winner_indicator = " 🏆" if votes == max(candidate_votes.values()) and votes > 0 else ""
                        self.stdout.write(f'    {candidate.user.get_full_name()}: {votes} votes ({percentage:.1f}%){winner_indicator}')
                        
                        if options['verbose']:
                            self.stdout.write(f'      Party: {candidate.party.name if candidate.party else "Independent"}')
                            self.stdout.write(f'      Student ID: {candidate.user.userprofile.student_id}')
                else:
                    self.stdout.write('  No votes cast yet.')
                
                # Show vote verification data
                if options['verbose']:
                    personal_votes = SchoolVote.objects.filter(
                        election=election,
                        position=position
                    ).count()
                    
                    anonymized_votes = AnonVote.objects.filter(
                        election=election,
                        position=position
                    ).count()
                    
                    self.stdout.write(f'  Personal Votes: {personal_votes}')
                    self.stdout.write(f'  Anonymized Votes: {anonymized_votes}')
                    
                    if personal_votes != anonymized_votes:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  Vote count mismatch detected!'
                            )
                        )
        
        # Overall statistics
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('Overall Statistics:')
        self.stdout.write(f'Total Elections: {SchoolElection.objects.count()}')
        self.stdout.write(f'Active Elections: {SchoolElection.objects.filter(is_active=True).count()}')
        self.stdout.write(f'Total Candidates: {Candidate.objects.count()}')
        self.stdout.write(f'Total Votes Cast: {SchoolVote.objects.count()}')
        self.stdout.write(f'Total Users: {User.objects.count()}')
        self.stdout.write(f'Verified Users: {UserProfile.objects.filter(is_verified=True).count()}')
