from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
from django.urls import reverse
import json
import csv

from election_module.models import SchoolElection, SchoolPosition
from candidate_module.models import Candidate
from voting_module.models import SchoolVote, VoteReceipt
from auth_module.models import UserProfile
from .models import ElectionResult, ResultChart, ResultExport
from .forms import ResultFilterForm, ChartConfigForm
from E_Botar.services.analytics import generate_election_results, calculate_statistics
from E_Botar.utils.logging_utils import log_activity


@login_required
def results_dashboard(request):
    """Results dashboard for viewing election results"""
    # Get completed elections
    completed_elections = SchoolElection.objects.filter(
        end_date__lt=timezone.now(),
        is_active=True
    ).order_by('-end_date')
    
    # Get active elections
    active_elections = SchoolElection.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        is_active=True
    ).order_by('-start_date')
    
    # Get upcoming elections
    upcoming_elections = SchoolElection.objects.filter(
        start_date__gt=timezone.now(),
        is_active=True
    ).order_by('start_date')
    
    context = {
        'completed_elections': completed_elections,
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'page_title': 'Election Results'
    }
    return render(request, 'result_module/results_dashboard.html', context)


@login_required
def election_results(request, election_id):
    """Display results for a specific election"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Check if election has ended or user is staff
    if not election.end_date < timezone.now() and not request.user.is_staff:
        messages.error(request, 'Results are not available yet.')
        return redirect('result_module:results_dashboard')
    
    # Generate results
    results = generate_election_results(election)
    
    # Get statistics
    statistics = calculate_statistics(election)
    
    # Get result charts
    charts = ResultChart.objects.filter(election=election).order_by('order')
    
    context = {
        'election': election,
        'results': results,
        'statistics': statistics,
        'charts': charts,
        'page_title': f'Results: {election.title}'
    }
    return render(request, 'result_module/election_results.html', context)


@login_required
def position_results(request, election_id, position_id):
    """Display results for a specific position"""
    election = get_object_or_404(SchoolElection, id=election_id)
    position = get_object_or_404(SchoolPosition, id=position_id)
    
    # Check if election has ended or user is staff
    if not election.end_date < timezone.now() and not request.user.is_staff:
        messages.error(request, 'Results are not available yet.')
        return redirect('result_module:results_dashboard')
    
    # Get votes for this position
    votes = SchoolVote.objects.filter(
        election=election,
        position=position
    ).values('candidate').annotate(
        vote_count=Count('id')
    ).order_by('-vote_count')
    
    # Get candidate details
    candidates_with_votes = []
    for vote in votes:
        candidate = Candidate.objects.get(id=vote['candidate'])
        candidates_with_votes.append({
            'candidate': candidate,
            'vote_count': vote['vote_count']
        })
    
    # Calculate total votes
    total_votes = sum(c['vote_count'] for c in candidates_with_votes)
    
    # Calculate percentages
    for candidate_data in candidates_with_votes:
        if total_votes > 0:
            candidate_data['percentage'] = (candidate_data['vote_count'] / total_votes) * 100
        else:
            candidate_data['percentage'] = 0
    
    context = {
        'election': election,
        'position': position,
        'candidates': candidates_with_votes,
        'total_votes': total_votes,
        'page_title': f'Results: {position.name} - {election.title}'
    }
    return render(request, 'result_module/position_results.html', context)


@staff_member_required
def generate_results(request, election_id):
    """Generate results for an election (staff only)"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    if request.method == 'POST':
        # Generate results
        results = generate_election_results(election)
        
        # Save results to database
        for position_id, position_results in results.items():
            position = SchoolPosition.objects.get(id=position_id)
            
            # Clear existing results
            ElectionResult.objects.filter(election=election, position=position).delete()
            
            # Save new results
            for candidate_data in position_results['candidates']:
                ElectionResult.objects.create(
                    election=election,
                    position=position,
                    candidate=candidate_data['candidate'],
                    vote_count=candidate_data['vote_count'],
                    percentage=candidate_data['percentage']
                )
        
        log_activity(
            user=request.user,
            action_type='results_generated',
            description=f'Generated results for election: {election.title}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Results generated successfully!')
        return redirect('result_module:election_results', election_id=election.id)
    
    context = {
        'election': election,
        'page_title': f'Generate Results: {election.title}'
    }
    return render(request, 'result_module/generate_results.html', context)


@login_required
def export_results(request, election_id):
    """Export results to CSV"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Check if election has ended or user is staff
    if not election.end_date < timezone.now() and not request.user.is_staff:
        messages.error(request, 'Results are not available yet.')
        return redirect('result_module:results_dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{election.title}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Election', 'Position', 'Candidate', 'Vote Count', 'Percentage'
    ])
    
    # Get results
    results = ElectionResult.objects.filter(election=election).select_related(
        'position', 'candidate'
    ).order_by('position__name', '-vote_count')
    
    for result in results:
        writer.writerow([
            election.title,
            result.position.name,
            result.candidate.user.get_full_name() or result.candidate.user.username,
            result.vote_count,
            f"{result.percentage:.2f}%"
        ])
    
    log_activity(
        user=request.user,
        action_type='results_exported',
        description=f'Exported results for election: {election.title}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return response


@login_required
def results_statistics(request, election_id):
    """Display detailed statistics for an election"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Check if election has ended or user is staff
    if not election.end_date < timezone.now() and not request.user.is_staff:
        messages.error(request, 'Results are not available yet.')
        return redirect('result_module:results_dashboard')
    
    # Get statistics
    statistics = calculate_statistics(election)
    
    # Get participation by position
    position_stats = []
    for position in election.positions.all():
        position_votes = SchoolVote.objects.filter(
            election=election,
            position=position
        ).count()
        position_stats.append({
            'position': position,
            'votes': position_votes
        })
    
    # Get voter demographics
    voter_demographics = UserProfile.objects.filter(
        user__school_votes__election=election
    ).values('department__name').annotate(
        count=Count('user', distinct=True)
    ).order_by('-count')
    
    context = {
        'election': election,
        'statistics': statistics,
        'position_stats': position_stats,
        'voter_demographics': voter_demographics,
        'page_title': f'Statistics: {election.title}'
    }
    return render(request, 'result_module/results_statistics.html', context)


@staff_member_required
def create_chart(request, election_id):
    """Create a chart for election results"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    if request.method == 'POST':
        form = ChartConfigForm(request.POST)
        if form.is_valid():
            chart = form.save(commit=False)
            chart.election = election
            chart.created_by = request.user
            chart.save()
            
            log_activity(
                user=request.user,
                action_type='chart_created',
                description=f'Created chart for election: {election.title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Chart created successfully!')
            return redirect('result_module:election_results', election_id=election.id)
    else:
        form = ChartConfigForm()
    
    context = {
        'election': election,
        'form': form,
        'page_title': f'Create Chart: {election.title}'
    }
    return render(request, 'result_module/create_chart.html', context)


@login_required
def results_comparison(request):
    """Compare results between elections"""
    elections = SchoolElection.objects.filter(
        end_date__lt=timezone.now(),
        is_active=True
    ).order_by('-end_date')
    
    # Get selected elections for comparison
    election_ids = request.GET.getlist('elections')
    selected_elections = elections.filter(id__in=election_ids) if election_ids else elections[:2]
    
    # Generate comparison data
    comparison_data = {}
    for election in selected_elections:
        results = generate_election_results(election)
        comparison_data[election.id] = {
            'election': election,
            'results': results
        }
    
    context = {
        'elections': elections,
        'selected_elections': selected_elections,
        'comparison_data': comparison_data,
        'page_title': 'Results Comparison'
    }
    return render(request, 'result_module/results_comparison.html', context)


@login_required
def results_api(request, election_id):
    """API endpoint for election results"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Check if election has ended or user is staff
    if not election.end_date < timezone.now() and not request.user.is_staff:
        return JsonResponse({'error': 'Results not available'}, status=403)
    
    # Generate results
    results = generate_election_results(election)
    
    # Get statistics
    statistics = calculate_statistics(election)
    
    return JsonResponse({
        'election': {
            'id': election.id,
            'title': election.title,
            'start_date': election.start_date.isoformat(),
            'end_date': election.end_date.isoformat(),
        },
        'results': results,
        'statistics': statistics
    })
