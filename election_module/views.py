from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Max
from django.core.paginator import Paginator
from django.urls import reverse

from .models import SchoolElection, SchoolPosition, ElectionPosition, Party
from .forms import ElectionForm, PositionForm, PartyForm
from candidate_module.models import Candidate, CandidateApplication
from auth_module.models import UserProfile, ActivityLog
from E_Botar.utils.logging_utils import log_activity


def election_list(request):
    """Display list of elections"""
    elections = SchoolElection.objects.filter(is_active=True).order_by('-created_at')
    
    # Check if user has voted in each election
    if request.user.is_authenticated:
        from voting_module.models import SchoolVote
        for election in elections:
            election.user_has_voted = SchoolVote.objects.filter(
                voter=request.user,
                election=election
            ).exists()
    else:
        for election in elections:
            election.user_has_voted = False
    
    context = {
        'elections': elections,
        'page_title': 'Active Elections',
        'now': timezone.now()
    }
    return render(request, 'Election_module/school_election_list.html', context)


def election_detail(request, election_id):
    """Display election details and positions"""
    election = get_object_or_404(SchoolElection, id=election_id)
    election_positions = election.positions.all().order_by('order')
    positions_with_candidates = []
    
    # Get candidates for each position
    for election_position in election_positions:
        position = election_position.position  # Get the actual SchoolPosition
        candidates = Candidate.objects.filter(
            position=position,
            election=election,
            is_active=True
        ).distinct()
        
        positions_with_candidates.append({
            'position': position,
            'candidates': candidates
        })
    
    context = {
        'election': election,
        'positions_with_candidates': positions_with_candidates,
        'page_title': f'Election: {election.title}'
    }
    return render(request, 'Election_module/school_election_detail.html', context)


@staff_member_required
def election_create(request):
    """Create a new election"""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            
            log_activity(
                user=request.user,
                action='election_created',
                description=f'Created election: {election.title}',
                request=request
            )
            
            messages.success(request, 'Election created successfully!')
            return redirect('election_module:election_detail', election_id=election.id)
    else:
        form = ElectionForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Election'
    }
    return render(request, 'Admin_module/election_form.html', context)


@staff_member_required
def election_edit(request, election_id):
    """Edit an existing election"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            
            log_activity(
                user=request.user,
                action='election_updated',
                description=f'Updated election: {election.title}',
                request=request
            )
            
            messages.success(request, 'Election updated successfully!')
            return redirect('election_module:election_detail', election_id=election.id)
    else:
        form = ElectionForm(instance=election)
    
    context = {
        'form': form,
        'election': election,
        'page_title': f'Edit Election: {election.title}'
    }
    return render(request, 'Admin_module/election_form.html', context)


@staff_member_required
def election_delete(request):
    """Delete an election (POST-only, id from body)"""
    if request.method != 'POST':
        return redirect('election_module:school_election_list')
    election_id = request.POST.get('election_id')
    election = get_object_or_404(SchoolElection, id=election_id)
    election_title = election.title
    election.delete()
    log_activity(
        user=request.user,
        action='election_deleted',
        description=f'Deleted election: {election_title}',
        request=request
    )
    messages.success(request, 'Election deleted successfully!')
    return redirect('election_module:school_election_list')


@staff_member_required
def position_list(request):
    """Display list of positions"""
    positions = SchoolPosition.objects.filter(is_active=True).order_by('display_order', 'name')
    
    # Get active election
    active_election = SchoolElection.objects.filter(is_active=True).first()
    
    # Add election availability info to each position
    positions_with_election_info = []
    for position in positions:
        position_info = {
            'position': position,
            'is_available_in_active_election': False,
            'election_status': 'Not available at the current election'
        }
        
        if active_election:
            # Check if position is associated with active election
            election_position = ElectionPosition.objects.filter(
                election=active_election,
                position=position
            ).first()
            
            if election_position:
                position_info['is_available_in_active_election'] = True
                position_info['election_status'] = f'Available in {active_election.title}'
            else:
                position_info['election_status'] = 'Not available at the current election'
        else:
            position_info['election_status'] = 'No active election'
        
        positions_with_election_info.append(position_info)
    
    context = {
        'positions': positions_with_election_info,
        'active_election': active_election,
        'page_title': 'Election Positions'
    }
    return render(request, 'Admin_module/positions_list.html', context)


@staff_member_required
def position_create(request):
    """Create a new position"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            
            # Automatically associate with active election
            active_election = SchoolElection.objects.filter(is_active=True).first()
            if active_election:
                # Get the next order number for this election
                max_order = ElectionPosition.objects.filter(election=active_election).aggregate(
                    max_order=Max('order')
                )['max_order'] or 0
                next_order = max_order + 1
                
                # Create ElectionPosition relationship
                ElectionPosition.objects.get_or_create(
                    election=active_election,
                    position=position,
                    defaults={'order': next_order}
                )
                log_activity(
                    user=request.user,
                    action='position_created',
                    description=f'Created position: {position.name} and associated with active election: {active_election.title}',
                    request=request
                )
                messages.success(request, f'Position created successfully and associated with active election: {active_election.title}!')
            else:
                log_activity(
                    user=request.user,
                    action='position_created',
                    description=f'Created position: {position.name} (no active election)',
                    request=request
                )
                messages.success(request, 'Position created successfully! (No active election to associate with)')
            
            return redirect('admin_module:positions_list')
    else:
        form = PositionForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Position',
        'positions_exist': SchoolPosition.objects.exists()
    }
    return render(request, 'Admin_module/position_form.html', context)


@staff_member_required
def position_edit(request, position_id):
    """Edit an existing position"""
    position = get_object_or_404(SchoolPosition, id=position_id)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            
            log_activity(
                user=request.user,
                action='position_updated',
                description=f'Updated position: {position.name}',
                request=request
            )
            
            messages.success(request, 'Position updated successfully!')
            return redirect('admin_module:positions_list')
    else:
        form = PositionForm(instance=position)
    
    context = {
        'form': form,
        'position': position,
        'page_title': f'Edit Position: {position.name}',
        'positions_exist': SchoolPosition.objects.exists()
    }
    return render(request, 'Admin_module/position_form.html', context)


@staff_member_required
def position_delete(request):
    """Delete a position (POST-only, id from body)"""
    if request.method != 'POST':
        return redirect('admin_module:positions_list')
    position_id = request.POST.get('position_id')
    position = get_object_or_404(SchoolPosition, id=position_id)
    position_name = position.name
    position.delete()
    log_activity(
        user=request.user,
        action='position_deleted',
        description=f'Deleted position: {position_name}',
        request=request
    )
    messages.success(request, 'Position deleted successfully!')
    return redirect('election_module:position_list')


@staff_member_required
def election_pause(request):
    """Pause an ongoing election (sets is_active=False)."""
    if request.method != 'POST':
        return redirect('election_module:school_election_list')
    election_id = request.POST.get('election_id')
    election = get_object_or_404(SchoolElection, id=election_id)
    election.is_active = False
    election.save()
    messages.success(request, f'Election "{election.title}" has been paused.')
    return redirect('admin_module:elections_list')


@staff_member_required
def election_resume(request):
    """Resume a paused election (sets is_active=True)."""
    if request.method != 'POST':
        return redirect('election_module:school_election_list')
    election_id = request.POST.get('election_id')
    election = get_object_or_404(SchoolElection, id=election_id)
    election.is_active = True
    election.save()
    messages.success(request, f'Election "{election.title}" has been resumed.')
    return redirect('admin_module:elections_list')


@staff_member_required
def election_end_now(request):
    """End the election immediately by setting end_date to now and deactivating it."""
    if request.method != 'POST':
        return redirect('election_module:school_election_list')
    election_id = request.POST.get('election_id')
    election = get_object_or_404(SchoolElection, id=election_id)
    election.end_date = timezone.now()
    election.is_active = False
    election.save()
    messages.success(request, f'Election "{election.title}" has been ended now.')
    return redirect('admin_module:elections_list')


@staff_member_required
def associate_position_with_election(request, position_id):
    """Associate a position with the active election"""
    position = get_object_or_404(SchoolPosition, id=position_id)
    active_election = SchoolElection.objects.filter(is_active=True).first()
    
    if not active_election:
        messages.error(request, 'No active election found!')
        return redirect('admin_module:positions_list')
    
    if request.method == 'POST':
        # Create ElectionPosition relationship
        election_position, created = ElectionPosition.objects.get_or_create(
            election=active_election,
            position=position,
            defaults={'order': position.display_order}
        )
        
        if created:
            log_activity(
                user=request.user,
                action='position_associated',
                description=f'Associated position: {position.name} with election: {active_election.title}',
                request=request
            )
            messages.success(request, f'Position "{position.name}" has been associated with "{active_election.title}"!')
        else:
            messages.info(request, f'Position "{position.name}" is already associated with "{active_election.title}"!')
        
        return redirect('admin_module:positions_list')
    
    context = {
        'position': position,
        'active_election': active_election,
        'page_title': f'Associate Position with Election'
    }
    return render(request, 'Admin_module/position_associate_confirm.html', context)


@staff_member_required
def fix_position_associations(request):
    """Fix all position associations with the active election"""
    active_election = SchoolElection.objects.filter(is_active=True).first()
    
    if not active_election:
        messages.error(request, 'No active election found!')
        return redirect('admin_module:positions_list')
    
    if request.method == 'POST':
        # Get all active positions
        positions = SchoolPosition.objects.filter(is_active=True)
        associated_count = 0
        
        for position in positions:
            # Check if position is already associated
            election_position = ElectionPosition.objects.filter(
                election=active_election,
                position=position
            ).first()
            
            if not election_position:
                # Get the next order number
                max_order = ElectionPosition.objects.filter(election=active_election).aggregate(
                    max_order=Max('order')
                )['max_order'] or 0
                next_order = max_order + 1
                
                # Create association
                ElectionPosition.objects.create(
                    election=active_election,
                    position=position,
                    order=next_order
                )
                associated_count += 1
        
        log_activity(
            user=request.user,
            action='positions_associations_fixed',
            description=f'Fixed associations for {associated_count} positions with election: {active_election.title}',
            request=request
        )
        
        if associated_count > 0:
            messages.success(request, f'Successfully associated {associated_count} positions with "{active_election.title}"!')
        else:
            messages.info(request, 'All positions are already associated with the active election.')
        
        return redirect('admin_module:positions_list')
    
    context = {
        'active_election': active_election,
        'page_title': 'Fix Position Associations'
    }
    return render(request, 'Admin_module/fix_associations_confirm.html', context)


@staff_member_required
def party_list(request):
    """Display list of parties"""
    parties = Party.objects.filter(is_active=True).order_by('name')
    
    context = {
        'parties': parties,
        'page_title': 'Political Parties'
    }
    return render(request, 'Admin_module/party_list.html', context)


@staff_member_required
def party_create(request):
    """Create a new party"""
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES)
        if form.is_valid():
            party = form.save()
            
            log_activity(
                user=request.user,
                action='party_created',
                description=f'Created party: {party.name}',
                request=request
            )
            
            messages.success(request, 'Party created successfully!')
            return redirect('election_module:party_list')
    else:
        form = PartyForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Party'
    }
    return render(request, 'Admin_module/party_form.html', context)


@staff_member_required
def party_edit(request, party_id):
    """Edit an existing party"""
    party = get_object_or_404(Party, id=party_id)
    
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES, instance=party)
        if form.is_valid():
            form.save()
            
            log_activity(
                user=request.user,
                action='party_updated',
                description=f'Updated party: {party.name}',
                request=request
            )
            
            messages.success(request, 'Party updated successfully!')
            return redirect('election_module:party_list')
    else:
        form = PartyForm(instance=party)
    
    context = {
        'form': form,
        'party': party,
        'page_title': f'Edit Party: {party.name}'
    }
    return render(request, 'Admin_module/party_form.html', context)


@staff_member_required
def election_statistics(request, election_id):
    """Display election statistics"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get basic statistics
    total_positions = election.positions.count()
    total_candidates = Candidate.objects.filter(
        election=election,
        is_active=True
    ).distinct().count()
    
    # Get voter statistics
    total_eligible_voters = UserProfile.objects.filter(is_verified=True).count()
    
    context = {
        'election': election,
        'total_positions': total_positions,
        'total_candidates': total_candidates,
        'total_eligible_voters': total_eligible_voters,
        'page_title': f'Statistics: {election.title}'
    }
    return render(request, 'Admin_module/election_statistics.html', context)


@staff_member_required
def update_positions_order(request):
    """Update SchoolPosition order via AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            order = data.get('order', [])
            
            for index, position_id in enumerate(order):
                SchoolPosition.objects.filter(id=position_id).update(display_order=index + 1)
            
            log_activity(
                user=request.user,
                action='positions_order_updated',
                description='Updated positions order',
                request=request
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@staff_member_required
def update_position_order(request):
    """Update position order via AJAX"""
    if request.method == 'POST':
        try:
            position_ids = request.POST.getlist('position_ids[]')
            election_id = request.POST.get('election_id')
            
            election = get_object_or_404(SchoolElection, id=election_id)
            
            for index, position_id in enumerate(position_ids):
                ElectionPosition.objects.filter(
                    election=election,
                    position_id=position_id
                ).update(order=index + 1)
            
            log_activity(
                user=request.user,
                action='position_order_updated',
                description=f'Updated position order for election: {election.title}',
                request=request
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def past_election_winners(request):
    """Display past elections with their winners"""
    from voting_module.models import SchoolVote
    
    past_elections = SchoolElection.objects.filter(
        end_date__lt=timezone.now()
    ).order_by('-end_date')
    
    # Get winners for each past election
    election_winners = []
    for election in past_elections:
        # Aggregate vote counts for this election
        votes_map = {
            row['candidate_id']: row['votes']
            for row in SchoolVote.objects.filter(election=election)
            .values('candidate_id')
            .annotate(votes=Count('id'))
        }
        
        winners = []
        for election_position in election.positions.all():
            position = election_position.position  # Get the actual SchoolPosition
            
            # Get all candidates for this position
            candidates = Candidate.objects.filter(
                position=position,
                election=election,
                is_active=True
            ).select_related('user', 'party', 'user__profile')
            
            # Find candidate with most votes
            top_candidate = None
            max_votes = 0
            for candidate in candidates:
                cand_votes = votes_map.get(candidate.id, 0)
                if cand_votes > max_votes:
                    max_votes = cand_votes
                    top_candidate = candidate
            
            if top_candidate and max_votes > 0:
                winners.append({
                    'position': position,
                    'winner': top_candidate,
                    'votes': max_votes
                })
        
        if winners:  # Only add elections that have winners
            election_winners.append({
                'election': election,
                'winners': winners
            })
    
    context = {
        'election_winners': election_winners,
        'page_title': 'Past Election Winners'
    }
    return render(request, 'Election_module/past_election_winners.html', context)