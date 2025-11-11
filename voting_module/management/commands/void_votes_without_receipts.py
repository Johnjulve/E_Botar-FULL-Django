"""
Management command to void votes that don't have corresponding receipts.
This is useful for cleaning up votes cast before the receipt system was properly working.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting_module.models import SchoolVote, VoteReceipt
from election_module.models import SchoolElection


class Command(BaseCommand):
    help = 'Void votes that do not have corresponding receipts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the voter to void votes for (optional - if not provided, affects all users)',
        )
        parser.add_argument(
            '--election-id',
            type=int,
            help='Election ID to void votes for (optional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        election_id = options.get('election_id')
        dry_run = options.get('dry_run', False)

        # Build the query
        votes_query = SchoolVote.objects.all()
        
        if username:
            try:
                user = User.objects.get(username=username)
                votes_query = votes_query.filter(voter=user)
                self.stdout.write(f"Filtering votes for user: {username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
                return
        
        if election_id:
            try:
                election = SchoolElection.objects.get(id=election_id)
                votes_query = votes_query.filter(election=election)
                self.stdout.write(f"Filtering votes for election: {election.title}")
            except SchoolElection.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Election with ID {election_id} not found"))
                return

        # Find votes without receipts
        votes_to_void = []
        for vote in votes_query.select_related('voter', 'election', 'candidate', 'position'):
            # Check if receipt exists for this voter and election
            receipt_exists = VoteReceipt.objects.filter(
                user=vote.voter,
                election=vote.election
            ).exists()
            
            if not receipt_exists:
                votes_to_void.append(vote)

        if not votes_to_void:
            self.stdout.write(self.style.SUCCESS("No votes without receipts found. All votes are valid!"))
            return

        # Display what will be voided
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.WARNING(f"Found {len(votes_to_void)} vote(s) without receipts:"))
        self.stdout.write("="*70)
        
        votes_by_user = {}
        for vote in votes_to_void:
            key = (vote.voter.username, vote.election.title)
            if key not in votes_by_user:
                votes_by_user[key] = []
            votes_by_user[key].append(vote)

        for (username, election_title), votes in votes_by_user.items():
            self.stdout.write(f"\n{username} - {election_title}:")
            for vote in votes:
                self.stdout.write(
                    f"  • {vote.position.name}: "
                    f"{vote.candidate.user.get_full_name()} "
                    f"(cast on {vote.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
                )

        if dry_run:
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.WARNING("DRY RUN - No votes were deleted"))
            self.stdout.write(self.style.WARNING(f"Would delete {len(votes_to_void)} vote(s)"))
            self.stdout.write("="*70)
            return

        # Confirm deletion
        self.stdout.write("\n" + "="*70)
        confirm = input(self.style.WARNING(
            f"Are you sure you want to DELETE {len(votes_to_void)} vote(s)? (yes/no): "
        ))
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR("Operation cancelled"))
            return

        # Delete the votes
        deleted_count = 0
        for vote in votes_to_void:
            vote.delete()
            deleted_count += 1

        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully voided {deleted_count} vote(s)"))
        self.stdout.write(self.style.SUCCESS("Users can now vote again in these elections"))
        self.stdout.write("="*70)

