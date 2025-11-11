from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Candidate, CandidateApplication
from .forms import CandidateForm, CandidateApplicationForm
from election_module.models import SchoolElection, SchoolPosition, Party
from auth_module.models import UserProfile


def check_profile_completion(user):
    """Check if user has completed their profile"""
    try:
        profile = UserProfile.objects.get(user=user)
        if not profile.course or not profile.department:
            return False, "Please complete your profile by selecting your course and department."
        return True, None
    except UserProfile.DoesNotExist:
        return False, "Please complete your profile first."


@login_required
def candidate_dashboard(request):
    """Candidate dashboard with statistics and quick actions"""
    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('candidate_module:candidate_profile')
    
    # Get user's applications
    user_applications = CandidateApplication.objects.filter(user=request.user).select_related(
        'position', 'election', 'party'
    ).order_by('-submitted_at')
    
    # Get user's approved candidates
    user_candidates = Candidate.objects.filter(user=request.user).select_related(
        'position', 'election', 'party'
    ).order_by('-created_at')
    
    # Get upcoming elections for application
    upcoming_elections = SchoolElection.objects.filter(
        is_active=True,
        start_date__gt=timezone.now()
    ).order_by('start_date')
    
    context = {
        'user_profile': user_profile,
        'user_candidates': user_candidates,
        'user_applications': user_applications,
        'upcoming_elections': upcoming_elections,
        'page_title': 'Candidate Dashboard'
    }
    return render(request, 'Candidate_module/candidate_dashboard.html', context)


@login_required
def candidate_profile(request):
    """Display user's own profile information (redirects to auth profile)"""
    return redirect('auth_module:profile')


@login_required
def view_candidate_profile(request, candidate_id):
    """View a specific candidate's public profile"""
    candidate = get_object_or_404(Candidate, id=candidate_id, is_active=True)
    
    # Get candidate statistics
    total_votes = candidate.vote_count()
    percentage = candidate.percentage()
    
    # Get elections this candidate participated in
    elections = SchoolElection.objects.filter(
        candidates=candidate,
        is_active=True
    ).order_by('-start_date')
    
    # Get recent votes (if any)
    recent_votes = []  # This would need to be implemented based on your voting system
    
    context = {
        'candidate': candidate,
        'total_votes': total_votes,
        'percentage': percentage,
        'elections': elections,
        'recent_votes': recent_votes,
        'page_title': f'{candidate.user.get_full_name()} - Candidate Profile'
    }
    return render(request, 'Candidate_module/candidate_profile.html', context)


@login_required
def edit_candidate_profile(request):
    """Edit candidate profile"""
    context = {
        'page_title': 'Edit Profile'
    }
    return render(request, 'Candidate_module/candidate_profile.html', context)


@login_required
def candidate_applications(request):
    """Display candidate applications"""
    user_applications = CandidateApplication.objects.filter(user=request.user).select_related(
        'position', 'election', 'party'
    ).order_by('-submitted_at')
    # Pagination
    paginator = Paginator(user_applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'applications': user_applications,  # Changed to match template
        'user_applications': user_applications,  # Keep for backward compatibility
        'page_obj': page_obj,
        'page_title': 'My Applications'
    }
    return render(request, 'Candidate_module/my_applications.html', context)


@login_required
def create_application(request):
    """Create new application"""
    # Check profile completion
    profile_complete, error_message = check_profile_completion(request.user)
    if not profile_complete:
        messages.warning(request, error_message)
        return redirect('auth_module:profile')
    
    # Check if user has profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('auth_module:profile')
    
    # Check if there are upcoming elections
    upcoming_elections = SchoolElection.objects.filter(
        is_active=True,
        start_date__gt=timezone.now()
    )
    
    if not upcoming_elections.exists():
        messages.warning(request, 'No upcoming elections available for application.')
        return render(request, 'Candidate_module/candidate_application.html', {
            'applications_closed': True,
            'page_title': 'Apply as Candidate'
        })
    
    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            
            # Handle profile picture option
            use_profile_picture = request.POST.get('use_profile_picture') == 'on'
            
            if use_profile_picture:
                if user_profile.avatar:
                    application.photo = user_profile.avatar
                else:
                    form.add_error(None, 'You do not have a profile picture. Please upload a photo.')
                    context = {
                        'form': form,
                        'user_profile': user_profile,
                        'upcoming_elections': upcoming_elections,
                        'page_title': 'Apply as Candidate'
                    }
                    return render(request, 'Candidate_module/candidate_application.html', context)
            elif not application.photo:
                form.add_error('photo', 'Please upload a photo or select to use your profile picture.')
                context = {
                    'form': form,
                    'user_profile': user_profile,
                    'upcoming_elections': upcoming_elections,
                    'page_title': 'Apply as Candidate'
                }
                return render(request, 'Candidate_module/candidate_application.html', context)
            
            # Check for existing application
            existing_application = CandidateApplication.objects.filter(
                user=request.user,
                position=application.position,
                election=application.election,
            ).first()
            
            if existing_application:
                form.add_error(None, 'You have already applied for this position in this election.')
                context = {
                    'form': form,
                    'user_profile': user_profile,
                    'upcoming_elections': upcoming_elections,
                    'page_title': 'Apply as Candidate'
                }
                return render(request, 'Candidate_module/candidate_application.html', context)
            
            try:
                application.save()
                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('candidate_module:candidate_applications')
            except Exception as e:
                form.add_error(None, f'Error submitting application: {str(e)}')
                context = {
                    'form': form,
                    'user_profile': user_profile,
                    'upcoming_elections': upcoming_elections,
                    'page_title': 'Apply as Candidate'
                }
                return render(request, 'Candidate_module/candidate_application.html', context)
        # If form is not valid, show errors
        # Note: Django cannot preserve file uploads across form submissions for security reasons
        # Users will need to re-upload if there are validation errors
        if 'photo' in request.FILES:
            messages.warning(request, 'Please re-upload your photo as form validation failed.')
    else:
        form = CandidateApplicationForm()
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'upcoming_elections': upcoming_elections,
        'page_title': 'Apply as Candidate'
    }
    return render(request, 'Candidate_module/candidate_application.html', context)


@login_required
def edit_application(request, application_id):
    """Edit application"""
    application = get_object_or_404(CandidateApplication, id=application_id, user=request.user)
    
    if application.status != 'pending':
        messages.error(request, 'You can only edit pending applications.')
        return redirect('candidate_module:candidate_applications')
    
    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been updated successfully!')
            return redirect('candidate_module:candidate_applications')
    else:
        form = CandidateApplicationForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
        'page_title': 'Edit Application'
    }
    return render(request, 'Candidate_module/candidate_application.html', context)


@login_required
def delete_application(request, application_id):
    """Delete application"""
    application = get_object_or_404(CandidateApplication, id=application_id, user=request.user)
    
    if application.status != 'pending':
        messages.error(request, 'You can only delete pending applications.')
        return redirect('candidate_module:candidate_applications')
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Your application has been deleted successfully!')
        return redirect('candidate_module:candidate_applications')
    
    context = {
        'application': application,
        'page_title': 'Delete Application'
    }
    return render(request, 'Candidate_module/candidate_application.html', context)


@login_required
def available_elections(request):
    """Show available elections for candidates"""
    elections = SchoolElection.objects.filter(is_active=True).order_by('-start_date')
    
    context = {
        'elections': elections,
        'page_title': 'Available Elections'
    }
    return render(request, 'Election_module/school_election_list.html', context)


@login_required
def election_detail(request, election_id):
    """Show election detail for candidates"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get positions for this election
    positions = SchoolPosition.objects.filter(
        elections__election=election,
        is_active=True
    ).distinct()
    
    # Get candidates for this election
    candidates = Candidate.objects.filter(
        election=election,
        is_active=True
    ).select_related('user', 'position', 'party')
    
    context = {
        'election': election,
        'positions': positions,
        'candidates': candidates,
        'page_title': f'{election.title} - Details'
    }
    return render(request, 'Election_module/school_election_detail.html', context)
