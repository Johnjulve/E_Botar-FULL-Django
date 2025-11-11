from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum, Prefetch
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from auth_module.models import UserProfile
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from .models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from .forms import VoteForm, VoteReceiptForm
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition
from auth_module.models import UserProfile, ActivityLog
from E_Botar.utils.logging_utils import log_activity
from E_Botar.services.security import encrypt_string as encrypt_data, decrypt_string as decrypt_data

def check_profile_completion(user):
    """Check if user has completed their profile"""
    try:
        profile = UserProfile.objects.get(user=user)
        if not profile.course or not profile.department:
            return False, "Please complete your profile by selecting your course and department."
        return True, None
    except UserProfile.DoesNotExist:
        return False, "Please complete your profile first."
        
def home_view(request):
    """Public home page showing current administration and election info"""
    now_ts = timezone.now()

    # Get current active election (on-going voting)
    current_election = SchoolElection.objects.filter(
        is_active=True,
        start_date__lte=now_ts,
        end_date__gte=now_ts,
    ).first()
    
    completed_election = SchoolElection.objects.filter(
        end_date__lt=now_ts,
    ).order_by('-end_date').first()
    
    # Extract year range from current election title
    administration_year = "2024-2025"  # Default fallback
    if current_election and current_election.title:
        import re
        # Match patterns like "SY 2025-2026" or "2025-2026"
        match = re.search(r'(?:SY\s+)?(\d{4})\s*[-–]\s*(\d{4})', current_election.title)
        if match:
            administration_year = f"{match.group(1)}-{match.group(2)}"
    elif completed_election and completed_election.title:
        import re
        # Fallback to completed election if no current election
        match = re.search(r'(?:SY\s+)?(\d{4})\s*[-–]\s*(\d{4})', completed_election.title)
        if match:
            administration_year = f"{match.group(1)}-{match.group(2)}"
    
    # Calculate winners from the completed election (current administration)
    previous_election_winners = []
    if completed_election:
        # Aggregate all vote counts for the completed election once
        votes_map = {
            row['candidate_id']: row['votes']
            for row in SchoolVote.objects.filter(election=completed_election)
            .values('candidate_id')
            .annotate(votes=Count('id'))
        }

        # Get positions from the completed election
        positions = SchoolPosition.objects.filter(
            elections__election=completed_election,
            is_active=True,
        ).distinct()

        for position in positions:
            # Get candidates for this position in the completed election
            candidates = Candidate.objects.filter(
                position=position,
                election=completed_election,
                is_active=True
            ).select_related('user', 'party').prefetch_related('user__profile')
            
            if candidates:
                # Find candidate with max votes
                top = None
                for cand in candidates:
                    cand_votes = votes_map.get(cand.id, 0)
                    if top is None or cand_votes > top['votes']:
                        top = {'candidate': cand, 'votes': cand_votes}
                if top and top['votes'] > 0:
                    previous_election_winners.append({
                        'position': position,
                        'candidate': top['candidate'],
                        'votes': top['votes'],
                    })

    # Get position sections for current election candidates
    position_sections = []
    total_candidates = 0
    positions = []
    
    if current_election:
        # Get all positions in the current election
        election_positions = current_election.positions.all().order_by('order')
        
        for election_position in election_positions:
            position = election_position.position
            positions.append(position)
            
            # Get active candidates for this position in the current election
            candidates = Candidate.objects.filter(
                election=current_election,
                position=position,
                is_active=True
            ).select_related('user', 'party').prefetch_related('user__profile')
            
            total_candidates += candidates.count()
            
            if candidates.exists():
                position_sections.append({
                    'position': position,
                    'candidates': candidates
                })

    # Get upcoming election
    upcoming_election = SchoolElection.objects.filter(
        start_date__gt=now_ts, 
        is_active=True
    ).order_by('start_date').first()

    # Get basic statistics
    total_users = UserProfile.objects.count()
    total_elections = SchoolElection.objects.count()
    total_votes = SchoolVote.objects.count()

    context = {
        'current_election': current_election,
        'completed_election': completed_election,
        'previous_election_winners': previous_election_winners,
        'position_sections': position_sections,
        'total_candidates': total_candidates,
        'positions': positions,
        'administration_year': administration_year,
        'upcoming_election': upcoming_election,
        'total_users': total_users,
        'total_elections': total_elections,
        'total_votes': total_votes,
        'user': request.user,
        'now': now_ts,
        'page_title': 'E-Botar - School Administration'
    }
    return render(request, 'voting_module/home.html', context)


def voting_dashboard(request):
    """Display voting dashboard. Anonymous users see public info only."""
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if not user_profile.is_verified:
                messages.warning(request, 'Your account must be verified before you can vote.')
                return redirect('auth_module:profile')
        except UserProfile.DoesNotExist:
            messages.warning(request, 'Please complete your profile before voting.')
            return redirect('candidate_module:candidate_profile')
    
    # Get active elections
    active_elections = SchoolElection.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('-created_at')
    
    # Get user's voting history (authenticated users only)
    user_votes = SchoolVote.objects.none()
    if request.user.is_authenticated:
        user_votes = SchoolVote.objects.filter(voter=request.user).select_related(
            'election', 'position', 'candidate'
        ).order_by('-created_at')
    
    context = {
        'elections': active_elections,  # Changed from 'active_elections' to 'elections'
        'user_votes': user_votes,
        'user_profile': user_profile,
        'page_title': 'Voting Dashboard',
        'now': timezone.now(),  # Added missing 'now' variable
    }
    return render(request, 'voting_module/voting_dashboard_test.html', context)


@login_required
def election_voting(request, election_id):
    """Display voting interface for a specific election"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Check profile completion
    profile_complete, error_message = check_profile_completion(request.user)
    if not profile_complete:
        messages.warning(request, error_message)
        return redirect('auth_module:profile')
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.is_verified:
            messages.error(request, 'Your account must be verified before you can vote.')
            return redirect('auth_module:profile')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile before voting.')
        return redirect('auth_module:profile')
    
    # Check if election is active
    if not election.is_active_now():
        messages.error(request, 'This election is not currently active.')
        return redirect('voting_module:voting_dashboard')
    
    # Check if user has already voted in this election
    existing_votes = SchoolVote.objects.filter(
        voter=request.user,
        election=election
    )
    
    has_voted = existing_votes.exists()
    
    # Get positions and candidates for this election
    election_positions = election.positions.all().order_by('order')
    positions_with_candidates = []
    
    for election_position in election_positions:
        position = election_position.position  # Get the actual SchoolPosition
        # Get candidates directly - they should already be approved via Candidate model
        candidates = Candidate.objects.filter(
            election=election,
            position=position,
            is_active=True
        ).select_related('user', 'party', 'user__profile')
        
        if candidates.exists():
            positions_with_candidates.append({
                'position': position,
                'candidates': candidates
            })
    
    context = {
        'election': election,
        'positions_with_candidates': positions_with_candidates,
        'has_voted': has_voted,
        'user_profile': user_profile,
        'page_title': f'Vote: {election.title}'
    }
    return render(request, 'Election_module/school_election_detail.html', context)


@login_required
@require_http_methods(["POST"])
def submit_vote(request, election_id):
    """Submit votes for an election"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.is_verified:
            return JsonResponse({'success': False, 'error': 'Account not verified'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'})
    
    # Check if election is active
    if not election.is_active_now():
        return JsonResponse({'success': False, 'error': 'Election not active'})
    
    # Check if user has already voted
    existing_votes = SchoolVote.objects.filter(
        voter=request.user,
        election=election
    )
    
    if existing_votes.exists():
        return JsonResponse({'success': False, 'error': 'Already voted'})
    
    try:
        # Get vote data from request
        vote_data = json.loads(request.body)
        votes = vote_data.get('votes', [])
        
        if not votes:
            return JsonResponse({'success': False, 'error': 'No votes submitted'})
        
        # Generate a single receipt code for all votes in this ballot
        from E_Botar.services.security import generate_vote_receipt_code
        receipt_code = generate_vote_receipt_code()
        
        # Use database transaction to ensure atomicity
        with transaction.atomic():
            # Validate and create votes
            created_votes = []
            
            for vote in votes:
                position_id = vote.get('position_id')
                candidate_id = vote.get('candidate_id')
                
                if not position_id or not candidate_id:
                    continue
                
                # Use try/except instead of get_object_or_404 to handle missing objects gracefully
                try:
                    position = SchoolPosition.objects.get(id=position_id)
                    candidate = Candidate.objects.get(id=candidate_id, is_active=True)
                except (SchoolPosition.DoesNotExist, Candidate.DoesNotExist):
                    # Skip invalid votes silently
                    continue
                
                # Validate candidate belongs to this election and position
                if candidate.election != election or candidate.position != position:
                    continue
                
                # Check for duplicate vote for this position (safety check)
                if any(v.position == position for v in created_votes):
                    continue
                
                # Create vote with receipt code
                school_vote = SchoolVote.objects.create(
                    voter=request.user,
                    candidate=candidate,
                    position=position,
                    election=election,
                    receipt_code=receipt_code
                )
                
                created_votes.append(school_vote)
            
            if not created_votes:
                return JsonResponse({'success': False, 'error': 'No valid votes submitted'})
            
            # Create vote receipt
            receipt = VoteReceipt.objects.create(
                user=request.user,
                election=election,
                receipt_code=receipt_code,
                encrypted_receipt_code=encrypt_data(receipt_code)
            )
            
            # Log activity
            log_activity(
                user=request.user,
                action='vote',
                description=f'Voted in election: {election.title}',
                request=request
            )
        
        # Transaction committed successfully
        return JsonResponse({
            'success': True,
            'receipt_code': receipt.receipt_code,
            'votes_count': len(created_votes)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error submitting vote: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'error': 'An error occurred while processing your vote'})


@login_required
def vote_receipt(request, election_id):
    """Display vote receipt"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get user's votes for this election
    user_votes = SchoolVote.objects.filter(
        voter=request.user,
        election=election
    ).select_related('candidate', 'position', 'candidate__user', 'candidate__party')
    
    if not user_votes.exists():
        messages.error(request, 'No votes found for this election.')
        return redirect('voting_module:my_voting_history')
    
    # Get receipt
    receipt = VoteReceipt.objects.filter(
        user=request.user,
        election=election
    ).first()
    
    # Format ballot items for the template
    ballot_items = []
    for vote in user_votes:
        ballot_items.append({
            'position': vote.position.name,
            'candidate': vote.candidate.user.get_full_name(),
            'party': vote.candidate.party.name if vote.candidate.party else None
        })
    
    # Get vote timestamp
    voted_at = user_votes.first().created_at if user_votes.exists() else None
    
    context = {
        'election': election,
        'ballot_items': ballot_items,
        'receipt_code': receipt.receipt_code if receipt else None,
        'voted_at': voted_at,
        'page_title': f'Vote Receipt: {election.title}'
    }
    return render(request, 'voting_module/my_ballot.html', context)


@login_required
def view_ballot_entry(request, election_id):
    """Entry point for the "View Ballot" button on results pages.

    Behaviour:
    - If the authenticated user already voted in the given election, redirect
      straight to their receipt page for that election.
    - Otherwise, redirect to their overall voting history page.
    """
    election = get_object_or_404(SchoolElection, id=election_id)

    user_has_voted = SchoolVote.objects.filter(
        voter=request.user,
        election=election,
    ).exists()

    if user_has_voted:
        return redirect('voting_module:vote_receipt', election_id=election.id)

    return redirect('voting_module:my_voting_history')


@login_required
def voting_history(request):
    """Display user's voting history"""
    # Get all votes for this user
    user_votes = SchoolVote.objects.filter(voter=request.user).select_related(
        'election', 'position', 'candidate'
    ).order_by('-created_at')
    
    # Group votes by election
    elections_voted = {}
    for vote in user_votes:
        election_id = vote.election.id
        if election_id not in elections_voted:
            # Get the receipt for this election
            receipt = VoteReceipt.objects.filter(
                user=request.user,
                election=vote.election
            ).first()
            
            elections_voted[election_id] = {
                'election': vote.election,
                'voted_at': vote.created_at,
                'receipt_code': receipt.receipt_code if receipt else vote.receipt_code,
            }
    
    # Convert to list and sort by date (newest first)
    history = sorted(
        elections_voted.values(),
        key=lambda x: x['voted_at'],
        reverse=True
    )
    
    context = {
        'history': history,
        'page_title': 'Voting History'
    }
    return render(request, 'voting_module/my_voting_history.html', context)


def election_results(request, election_id):
    """Display election results - accessible to all users"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get results for each position
    election_positions = election.positions.all().order_by('order')
    results = {}
    
    for election_position in election_positions:
        position = election_position.position  # Get the actual SchoolPosition
        
        # First, get all candidates for this position in this election
        all_candidates = Candidate.objects.filter(
            election=election,
            position=position,
            is_active=True
        ).select_related('user', 'party')
        
        # Get vote counts for each candidate
        vote_counts = SchoolVote.objects.filter(
            election=election,
            position=position
        ).values('candidate').annotate(
            vote_count=Count('id')
        ).order_by('-vote_count')
        
        # Create a map of vote counts
        vote_map = {vc['candidate']: vc['vote_count'] for vc in vote_counts}
        total_position_votes = sum(vc['vote_count'] for vc in vote_counts)
        
        # Get candidate details with percentages
        candidates_with_votes = []
        for candidate in all_candidates:
            vote_count = vote_map.get(candidate.id, 0)
            percentage = (vote_count / total_position_votes * 100) if total_position_votes > 0 else 0
            candidates_with_votes.append({
                'candidate': candidate,
                'vote_count': vote_count,
                'percentage': round(percentage, 1)
            })
        
        # Sort candidates by vote count (highest first)
        candidates_with_votes.sort(key=lambda x: x['vote_count'], reverse=True)
        
        # Use position object as key (template expects this)
        results[position] = {
            'position': position,
            'candidates': candidates_with_votes,
            'total_votes': total_position_votes
        }
    
    context = {
        'election': election,
        'results': results,
        'page_title': f'Results: {election.title}'
    }
    return render(request, 'Election_module/school_election_results.html', context)


@staff_member_required
def voting_statistics(request, election_id):
    """Display voting statistics (staff only)"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get basic statistics
    total_votes = SchoolVote.objects.filter(election=election).count()
    total_voters = SchoolVote.objects.filter(election=election).values('voter').distinct().count()
    total_eligible_voters = UserProfile.objects.filter(is_verified=True).count()
    
    # Get participation by position
    position_stats = []
    for election_position in election.positions.all():
        position = election_position.position  # Get the actual SchoolPosition
        position_votes = SchoolVote.objects.filter(
            election=election,
            position=position
        ).count()
        position_stats.append({
            'position': position,
            'votes': position_votes
        })
    
    context = {
        'election': election,
        'total_votes': total_votes,
        'total_voters': total_voters,
        'total_eligible_voters': total_eligible_voters,
        'participation_rate': (total_voters / total_eligible_voters * 100) if total_eligible_voters > 0 else 0,
        'position_stats': position_stats,
        'page_title': f'Statistics: {election.title}'
    }
    return render(request, 'Result_module/voting_statistics.html', context)


@login_required
def verify_receipt(request):
    """Verify vote receipt"""
    if request.method == 'POST':
        form = VoteReceiptForm(request.POST)
        if form.is_valid():
            receipt_code = form.cleaned_data['receipt_code']
            
            # Find receipt
            receipt = VoteReceipt.objects.filter(
                receipt_code=receipt_code
            ).first()
            
            if receipt:
                # Get votes for this receipt
                votes = SchoolVote.objects.filter(
                    election=receipt.election,
                    receipt_code=receipt_code
                ).select_related('candidate', 'position')
                
                context = {
                    'receipt': receipt,
                    'votes': votes,
                    'verified': True
                }
                return render(request, 'voting_module/my_ballot.html', context)
            else:
                messages.error(request, 'Receipt not found.')
    else:
        form = VoteReceiptForm()
    
    context = {
        'form': form,
        'page_title': 'Verify Vote Receipt'
    }
    return render(request, 'voting_module/my_ballot.html', context)
