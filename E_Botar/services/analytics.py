from __future__ import annotations

from collections import defaultdict
from typing import Dict, Any, List
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Import models from consolidated modules
from election_module.models import SchoolElection, SchoolPosition, ElectionPosition
from candidate_module.models import Candidate
from voting_module.models import AnonVote, SchoolVote
from auth_module.models import UserProfile


def tally_election(election: SchoolElection) -> Dict[Any, dict]:
    """
    Compute per-position tallies for an election using anonymized votes.
    Returns dict keyed by position with:
      { 'candidates': [{candidate, vote_count, percentage}], 'total_votes': int }
    """
    positions = SchoolPosition.objects.filter(
        elections__election=election, 
        is_active=True
    ).prefetch_related('candidates')
    
    results: Dict[Any, dict] = {}
    
    for position in positions:
        candidates = Candidate.objects.filter(
            election=election,
            position=position,
            is_active=True
        )
        
        total_votes = 0
        counts: Dict[int, int] = defaultdict(int)
        
        for candidate in candidates:
            cnt = AnonVote.objects.filter(
                candidate=candidate, 
                election=election
            ).count()
            counts[candidate.id] = cnt
            total_votes += cnt
        
        rows = []
        for candidate in candidates:
            cnt = counts[candidate.id]
            pct = round((cnt / total_votes * 100), 1) if total_votes > 0 else 0
            rows.append({
                'candidate': candidate, 
                'vote_count': cnt, 
                'percentage': pct
            })
        
        rows.sort(key=lambda x: x['vote_count'], reverse=True)
        results[position] = {
            'candidates': rows, 
            'total_votes': total_votes
        }
    
    return results


def generate_election_results(election: SchoolElection) -> Dict[int, dict]:
    """Wrapper producing results keyed by position id for consumers in result_module."""
    by_position = tally_election(election)
    normalized: Dict[int, dict] = {}
    for position, data in by_position.items():
        # ensure key is id and structure stays the same
        normalized[position.id] = {
            'candidates': data['candidates'],
            'total_votes': data['total_votes'],
        }
    return normalized


def get_election_statistics(election: SchoolElection) -> dict:
    """Get comprehensive election statistics"""
    total_voters = UserProfile.objects.count()
    total_votes_cast = SchoolVote.objects.filter(election=election).count()
    participation_rate = (total_votes_cast / total_voters * 100) if total_voters > 0 else 0
    
    positions_count = ElectionPosition.objects.filter(election=election).count()
    candidates_count = Candidate.objects.filter(election=election).count()
    
    return {
        'total_voters': total_voters,
        'total_votes_cast': total_votes_cast,
        'participation_rate': round(participation_rate, 2),
        'positions_count': positions_count,
        'candidates_count': candidates_count,
        'election_status': 'Active' if election.is_active else 'Inactive',
        'time_remaining': _get_time_remaining(election)
    }


def calculate_statistics(election: SchoolElection) -> dict:
    """Compatibility wrapper used by result_module."""
    return get_election_statistics(election)


def _get_time_remaining(election: SchoolElection) -> str:
    """Get time remaining for election"""
    now = timezone.now()
    
    if election.start_date > now:
        delta = election.start_date - now
        return f"Starts in {delta.days} days, {delta.seconds // 3600} hours"
    elif election.end_date > now:
        delta = election.end_date - now
        return f"Ends in {delta.days} days, {delta.seconds // 3600} hours"
    else:
        return "Election ended"


def get_position_results(election: SchoolElection, position: SchoolPosition) -> dict:
    """Get detailed results for a specific position"""
    candidates = Candidate.objects.filter(
        election=election,
        position=position
    ).annotate(
        vote_count=Count('anonvotes', filter=Q(anonvotes__election=election))
    ).order_by('-vote_count')
    
    total_votes = sum(c.vote_count for c in candidates)
    
    results = []
    for candidate in candidates:
        percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'candidate': candidate,
            'vote_count': candidate.vote_count,
            'percentage': round(percentage, 2),
            'is_winner': candidate.vote_count == max(c.vote_count for c in candidates) and candidate.vote_count > 0
        })
    
    return {
        'position': position,
        'total_votes': total_votes,
        'candidates': results,
        'winner': results[0] if results and results[0]['is_winner'] else None
    }


def get_voting_trends(election: SchoolElection, days_back: int = 7) -> List[dict]:
    """Get voting trends over time"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Get daily vote counts
    daily_votes = []
    for i in range(days_back):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        vote_count = SchoolVote.objects.filter(
            election=election,
            created_at__gte=date,
            created_at__lt=next_date
        ).count()
        
        daily_votes.append({
            'date': date.strftime('%Y-%m-%d'),
            'votes': vote_count
        })
    
    return daily_votes


def generate_election_report(election: SchoolElection) -> dict:
    """Generate comprehensive election report"""
    statistics = get_election_statistics(election)
    results = tally_election(election)
    trends = get_voting_trends(election)
    
    return {
        'election': election,
        'statistics': statistics,
        'results': results,
        'trends': trends,
        'generated_at': timezone.now()
    }


def export_results_to_csv(election: SchoolElection) -> str:
    """Export election results to CSV format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Position', 'Candidate', 'Party', 'Votes', 'Percentage'])
    
    results = tally_election(election)
    
    for position, data in results.items():
        for candidate_data in data['candidates']:
            candidate = candidate_data['candidate']
            writer.writerow([
                position.name,
                candidate.user.get_full_name(),
                candidate.party.name if candidate.party else 'Independent',
                candidate_data['vote_count'],
                candidate_data['percentage']
            ])
    
    return output.getvalue()
