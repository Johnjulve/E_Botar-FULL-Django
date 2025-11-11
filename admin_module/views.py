from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Value, F
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import csv
import json
import random

from auth_module.models import UserProfile, Department, Course, ActivityLog
from candidate_module.models import Candidate, CandidateApplication
from election_module.models import SchoolElection, SchoolPosition, Party
from voting_module.models import SchoolVote, VoteReceipt
from .forms import UserCreationForm, BulkUserImportForm, ElectionManagementForm, DepartmentForm, CourseForm, DepartmentCSVImportForm, CourseCSVImportForm
from E_Botar.utils.logging_utils import log_activity
from E_Botar.services.email import EmailService


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with user management interface"""
    # Handle AJAX request for user data
    get_user_id = request.GET.get('get_user_data')
    if get_user_id:
        try:
            user = get_object_or_404(User, id=get_user_id)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                },
                'profile': {
                    'student_id': profile.student_id or '',
                    'year_level': profile.year_level or '',
                    'course_id': profile.course.id if profile.course else '',
                    'is_verified': profile.is_verified,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get users with their profiles
    users = (
        UserProfile.objects
        .select_related('user', 'department', 'course')
        .annotate(full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name')))
        .order_by('-created_at')
    )
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )
    
    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter == 'student':
        users = users.filter(user__is_staff=False, user__is_superuser=False)
    elif role_filter == 'staff':
        users = users.filter(user__is_staff=True, user__is_superuser=False)
    elif role_filter == 'superuser':
        users = users.filter(user__is_superuser=True)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users = users.filter(user__is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(user__is_active=False)
    
    # Filter by verification status
    verified_filter = request.GET.get('verified')
    if verified_filter == 'verified':
        users = users.filter(is_verified=True)
    elif verified_filter == 'unverified':
        users = users.filter(is_verified=False)
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get departments for the modal form
    departments = Department.objects.filter(is_active=True).prefetch_related('courses').order_by('name')
    
    context = {
        'rows': page_obj,  # Template expects 'rows' variable
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'verified_filter': verified_filter,
        'departments': departments,
        'page_title': 'Admin Users'
    }
    return render(request, 'Admin_module/admin_dashboard.html', context)


@staff_member_required
def user_management(request):
    """User management interface"""
    users = (
        UserProfile.objects
        .select_related('user', 'department', 'course')
        .annotate(full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name')))
        .order_by('-created_at')
    )
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )
    
    # Filter by verification status
    verification_status = request.GET.get('verification_status')
    if verification_status == 'verified':
        users = users.filter(is_verified=True)
    elif verification_status == 'unverified':
        users = users.filter(is_verified=False)
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'verification_status': verification_status,
        'page_title': 'User Management'
    }
    return render(request, 'Admin_module/candidates_list.html', context)


@staff_member_required
def create_user(request):
    """Create a new user"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            log_activity(
                user=request.user,
                action='user_created',
                description=f'Created user: {user.username}',
                request=request
            )
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('admin_module:user_management')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Create New User'
    }
    return render(request, 'Admin_module/create_user.html', context)


@staff_member_required
def user_detail(request, user_id):
    """Display user details"""
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    # Get user's activities
    activities = ActivityLog.objects.filter(user=user_profile.user).order_by('-timestamp')[:20]
    
    # Get user's votes
    votes = SchoolVote.objects.filter(voter=user_profile.user).select_related(
        'election', 'position', 'candidate'
    ).order_by('-created_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'activities': activities,
        'votes': votes,
        'page_title': f'User Details: {user_profile.user.username}'
    }
    return render(request, 'Admin_module/user_detail.html', context)


@staff_member_required
def bulk_user_import(request):
    """Bulk import/update users from CSV with overwrite options"""
    if request.method == 'POST':
        form = BulkUserImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            update_existing = form.cleaned_data.get('update_existing', True)
            overwrite_data = form.cleaned_data.get('overwrite_data', True)
            
            try:
                # Process CSV file
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(decoded_file.splitlines())
                
                created_count = 0
                updated_count = 0
                skipped_count = 0
                error_count = 0
                errors = []
                results = []
                
                for row_num, row in enumerate(csv_data, start=2):  # Start at 2 for header
                    try:
                        # Check if user already exists (by username or email)
                        existing_user = None
                        if row.get('username'):
                            existing_user = User.objects.filter(username=row['username']).first()
                        if not existing_user and row.get('email'):
                            existing_user = User.objects.filter(email=row['email']).first()
                        
                        if existing_user and not update_existing:
                            # Skip existing users if update_existing is False
                            skipped_count += 1
                            continue
                        
                        # Get or create department and course
                        department = None
                        course = None
                        
                        if row.get('department_code'):
                            try:
                                department = Department.objects.get(code=row['department_code'])
                            except Department.DoesNotExist:
                                errors.append(f'Row {row_num}: Department with code "{row["department_code"]}" not found')
                                error_count += 1
                                continue
                        
                        if row.get('course_code'):
                            try:
                                course = Course.objects.get(code=row['course_code'])
                            except Course.DoesNotExist:
                                errors.append(f'Row {row_num}: Course with code "{row["course_code"]}" not found')
                                error_count += 1
                                continue
                        
                        if existing_user:
                            # Update existing user
                            if overwrite_data:
                                # Overwrite user data with CSV data
                                existing_user.first_name = row.get('first_name', existing_user.first_name)
                                existing_user.last_name = row.get('last_name', existing_user.last_name)
                                existing_user.email = row.get('email', existing_user.email)
                                existing_user.save()
                                
                                # Update or create profile
                                profile, created = UserProfile.objects.get_or_create(
                                    user=existing_user,
                                    defaults={
                                        'student_id': row.get('student_id', ''),
                                        'department': department,
                                        'course': course,
                                        'year_level': row.get('year_level', ''),
                                        'phone_number': row.get('phone_number', ''),
                                        'is_verified': True
                                    }
                                )
                                
                                if not created and overwrite_data:
                                    # Overwrite profile data
                                    profile.student_id = row.get('student_id', profile.student_id)
                                    profile.department = department or profile.department
                                    profile.course = course or profile.course
                                    profile.year_level = row.get('year_level', profile.year_level)
                                    profile.phone_number = row.get('phone_number', profile.phone_number)
                                    profile.is_verified = True
                                    profile.save()
                                
                                updated_count += 1
                                results.append({
                                    'row': row_num,
                                    'username': existing_user.username,
                                    'email': existing_user.email,
                                    'first_name': existing_user.first_name,
                                    'last_name': existing_user.last_name,
                                    'status': 'updated',
                                    'password': ''
                                })
                            else:
                                # Skip if not overwriting
                                skipped_count += 1
                        else:
                            # Create new user
                            user = User.objects.create_user(
                                username=row['username'],
                                email=row['email'],
                                first_name=row.get('first_name', ''),
                                last_name=row.get('last_name', ''),
                                password=row.get('password', 'defaultpassword123')
                            )
                            
                            UserProfile.objects.create(
                                user=user,
                                student_id=row.get('student_id', ''),
                                department=department,
                                course=course,
                                year_level=row.get('year_level', ''),
                                phone_number=row.get('phone_number', ''),
                                is_verified=True
                            )
                            
                            created_count += 1
                            results.append({
                                'row': row_num,
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'status': 'created',
                                'password': row.get('password', 'defaultpassword123')
                            })
                        
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                        error_count += 1
                
                # Prepare result message
                result_message = f"Import completed: {created_count} created, {updated_count} updated, {skipped_count} skipped, {error_count} errors"
                
                if created_count > 0 or updated_count > 0:
                    messages.success(request, result_message)
                
                if errors:
                    for error in errors[:10]:  # Show first 10 errors
                        messages.error(request, error)
                    if len(errors) > 10:
                        messages.warning(request, f'... and {len(errors) - 10} more errors.')
                
                # Log the import activity
                log_activity(
                    user=request.user,
                    action='admin_action',
                    description=f'Bulk user import finished',
                    request=request,
                    additional_data={'created': created_count, 'updated': updated_count, 'skipped': skipped_count, 'errors': error_count}
                )
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('admin_module:bulk_user_import')

            # On success, re-render the tools page with results visible
            all_users = User.objects.all().order_by('username')[:100]
            context = {
                'form': BulkUserImportForm(),
                'page_title': 'Bulk User Import',
                'results': results,
                'all_users': all_users,
            }
            return render(request, 'Admin_module/admin_user_tools.html', context)
    else:
        form = BulkUserImportForm()
    
    context = {
        'form': form,
        'page_title': 'Bulk User Import'
    }
    return render(request, 'Admin_module/admin_user_tools.html', context)


@staff_member_required
def export_users(request):
    """Export users to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Email', 'First Name', 'Last Name', 'Student ID',
        'Department', 'Course', 'Year Level', 'Phone Number', 'Verified'
    ])
    
    users = UserProfile.objects.select_related('user', 'department', 'course')
    for user_profile in users:
        writer.writerow([
            user_profile.user.username,
            user_profile.user.email,
            user_profile.user.first_name,
            user_profile.user.last_name,
            user_profile.student_id,
            (user_profile.department.name if user_profile.department else ''),
            (user_profile.course.name if user_profile.course else ''),
            user_profile.year_level,
            user_profile.phone_number,
            'Yes' if user_profile.is_verified else 'No'
        ])
    
    # Record audit trail for export action
    log_activity(
        user=request.user,
        action='admin_action',
        description='Exported users to CSV',
        request=request,
        additional_data={'resource': 'users', 'format': 'csv'}
    )
    
    return response


@staff_member_required
def election_management(request):
    """Election management interface"""
    elections = SchoolElection.objects.order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        elections = elections.filter(title__icontains=search_query)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        elections = elections.filter(is_active=True)
    elif status_filter == 'inactive':
        elections = elections.filter(is_active=False)
    
    # Paginate results
    paginator = Paginator(elections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Election Management'
    }
    return render(request, 'Admin_module/elections_list.html', context)


@staff_member_required
def candidate_management(request):
    """Candidate management interface"""
    candidates = Candidate.objects.select_related(
        'user', 'user__profile', 'user__profile__course', 'user__profile__department',
        'party', 'position', 'election'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        candidates = candidates.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__profile__course__name__icontains=search_query) |
            Q(user__profile__year_level__icontains=search_query)
        )
    
    # Filter by party
    party_filter = request.GET.get('party')
    if party_filter:
        candidates = candidates.filter(party_id=party_filter)
    
    # Filter by position
    selected_position = request.GET.get('position')
    if selected_position:
        candidates = candidates.filter(position_id=selected_position)
    
    # Paginate results
    paginator = Paginator(candidates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get parties for filter dropdown
    parties = Party.objects.filter(is_active=True)
    
    # Get positions for filter dropdown
    from election_module.models import SchoolPosition
    positions = SchoolPosition.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'candidates': page_obj,  # template expects 'candidates'
        'search_query': search_query,
        'party_filter': party_filter,
        'parties': parties,
        'positions': positions,
        'selected_position': selected_position,
        'page_title': 'Candidate Management'
    }
    return render(request, 'Admin_module/candidates_list.html', context)


@staff_member_required
def review_applications(request):
    """Review candidate applications"""
    applications = CandidateApplication.objects.filter(
        status='pending'
    ).select_related('user', 'position', 'election').order_by('-submitted_at')
    
    # Paginate results
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_pending = CandidateApplication.objects.filter(status='pending').count()
    total_approved = CandidateApplication.objects.filter(status='approved').count()
    total_rejected = CandidateApplication.objects.filter(status='rejected').count()
    
    context = {
        'page_obj': page_obj,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'page_title': 'Review Applications'
    }
    return render(request, 'Admin_module/review_applications.html', context)


@staff_member_required
@require_http_methods(["POST"])
def approve_application(request, application_id):
    """Approve a candidate application"""
    application = get_object_or_404(CandidateApplication, id=application_id)
    
    if application.status == 'pending':
        application.status = 'approved'
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.save()
        
        # Create the actual Candidate record from the approved application
        candidate, created = Candidate.objects.get_or_create(
            user=application.user,
            election=application.election,
            position=application.position,
            defaults={
                'party': application.party,
                'manifesto': application.manifesto,
                'photo': application.photo,
                'is_active': True,
                'approved_application': application
            }
        )
        
        if created:
            log_activity(
                user=request.user,
                action='candidate_created',
                description=f'Created candidate {candidate.user.get_full_name()} for {candidate.position.name} from approved application',
                request=request
            )
        
        log_activity(
            user=request.user,
            action='application_approved',
            description=f'Approved application for {application.user.get_full_name()} for {application.position.name}',
            request=request
        )
        
        # Send email notification
        EmailService.send_system_notification(
            users=[application.user],
            subject='Application Approved',
            message=f'Your application for {application.position.name} has been approved! You are now an official candidate.',
            notification_type='success'
        )
        
        messages.success(request, f'Application approved and candidate {candidate.user.get_full_name()} created successfully!')
    else:
        messages.error(request, 'Application is not pending.')
    
    return redirect('admin_module:review_applications')


@staff_member_required
@require_http_methods(["POST"])
def reject_application(request, application_id):
    """Reject a candidate application"""
    application = get_object_or_404(CandidateApplication, id=application_id)
    
    if application.status == 'pending':
        application.status = 'rejected'
        application.save()
        
        log_activity(
            user=request.user,
            action='application_rejected',
            description=f'Rejected application for {application.user.get_full_name()} for {application.position.name}',
            request=request
        )
        
        # Send email notification
        EmailService.send_system_notification(
            users=[application.user],
            subject='Application Rejected',
            message=f'Your application for {application.position.name} has been rejected.',
            notification_type='warning'
        )
        
        messages.success(request, 'Application rejected.')
    else:
        messages.error(request, 'Application is not pending.')
    
    return redirect('admin_module:review_applications')


@staff_member_required
def activity_logs(request):
    """Display system activity logs"""
    activities = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        activities = activities.filter(user_id=user_filter)
    
    # Filter by action type
    action_filter = request.GET.get('action_type')
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        activities = activities.filter(timestamp__date__gte=date_from)
    if date_to:
        activities = activities.filter(timestamp__date__lte=date_to)
    
    # Paginate results
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users for filter dropdown
    users = User.objects.filter(is_active=True).order_by('username')
    
    # Get action types for filter dropdown
    action_types = ActivityLog.ACTION_TYPES
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'action_types': action_types,
        'current_filters': {
            'user': user_filter,
            'action_type': action_filter,
            'date_from': date_from,
            'date_to': date_to,
        },
        'page_title': 'Activity Logs'
    }
    return render(request, 'Admin_module/activity_logs.html', context)


@staff_member_required
def system_statistics(request):
    """Display system statistics"""
    # User statistics
    total_users = UserProfile.objects.count()
    verified_users = UserProfile.objects.filter(is_verified=True).count()
    unverified_users = total_users - verified_users
    
    # Election statistics
    total_elections = SchoolElection.objects.count()
    active_elections = SchoolElection.objects.filter(is_active=True).count()
    completed_elections = SchoolElection.objects.filter(
        end_date__lt=timezone.now()
    ).count()
    
    # Voting statistics
    total_votes = SchoolVote.objects.count()
    unique_voters = SchoolVote.objects.values('voter').distinct().count()
    
    # Candidate statistics
    total_candidates = Candidate.objects.count()
    approved_applications = CandidateApplication.objects.filter(status='approved').count()
    pending_applications = CandidateApplication.objects.filter(status='pending').count()
    
    context = {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'total_elections': total_elections,
        'active_elections': active_elections,
        'completed_elections': completed_elections,
        'total_votes': total_votes,
        'unique_voters': unique_voters,
        'total_candidates': total_candidates,
        'approved_applications': approved_applications,
        'pending_applications': pending_applications,
        'page_title': 'System Statistics'
    }
    return render(request, 'Admin_module/administration_dashboard.html', context)


@staff_member_required
def candidate_create(request):
    """Create a new candidate application (admin-assisted)"""
    from .forms import CandidateApplicationForm
    from django.utils import timezone
    
    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            
            # Log the activity
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Created candidate application for {application.user.get_full_name()} for {application.position.name}',
                request=request
            )
            
            messages.success(
                request, 
                f'Candidate application created successfully for {application.user.get_full_name()}! '
                f'The application is now pending review and can be found in "Review Applications".'
            )
            return redirect('admin_module:review_applications')
        # If form validation fails, it will fall through to render with errors
        # Django forms handle file upload persistence in the form instance
    else:
        form = CandidateApplicationForm()
    
    # Get current election info for context
    now = timezone.now()
    current_election = SchoolElection.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
    ).first()
    
    context = {
        'form': form,
        'page_title': 'Create Candidate Application',
        'current_election': current_election,
        'available_users': User.objects.filter(is_active=True).order_by('first_name', 'last_name')[:10],  # Show first 10 users as examples
    }
    return render(request, 'Admin_module/candidate_form.html', context)


@staff_member_required
def candidate_edit(request, candidate_id):
    """Edit an existing candidate"""
    from .forms import CandidateManagementForm
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    if request.method == 'POST':
        form = CandidateManagementForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully!')
            return redirect('admin_module:candidates_list')
    else:
        form = CandidateManagementForm(instance=candidate)
    
    context = {
        'candidate': candidate,
        'form': form,
        'page_title': 'Edit Candidate'
    }
    return render(request, 'Admin_module/candidate_edit.html', context)


@staff_member_required
def candidate_delete(request):
    """Delete a candidate (POST-only, id from body)"""
    if request.method != 'POST':
        return redirect('admin_module:candidates_list')
    candidate_id = request.POST.get('candidate_id')
    reason = (request.POST.get('reason') or '').strip()
    if not reason:
        messages.error(request, 'Please provide a memo/reason for deleting or disqualifying the candidate.')
        return redirect('admin_module:candidates_list')
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate_name = candidate.user.get_full_name()
    position_name = candidate.position.name if candidate.position else 'N/A'
    candidate.delete()

    # Audit trail with memo reason
    log_activity(
        user=request.user,
        action='candidate_deleted',
        description=f'Deleted candidate {candidate_name} ({position_name})',
        request=request,
        additional_data={'reason': reason, 'candidate_id': candidate_id}
    )

    # Notify the candidate (user side)
    try:
        EmailService.send_system_notification(
            users=[User.objects.get(id=candidate.user.id)],
            subject='Candidacy Update: Disqualification/Removal',
            message=(
                f'Dear {candidate_name},\n\n'
                f'Your candidacy for {position_name} has been removed/disqualified.\n'
                f'Reason: {reason}\n\n'
                f'If you believe this is in error, please contact the election administrators.'
            ),
            notification_type='warning'
        )
    except Exception:
        # Non-fatal; continue even if email fails
        pass

    messages.success(request, f'Candidate deleted. Memo recorded: {reason}')
    return redirect('admin_module:candidates_list')


@staff_member_required
def elections_list(request):
    """List all elections"""
    elections = SchoolElection.objects.all().order_by('-created_at')
    
    # Paginate results
    paginator = Paginator(elections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Elections List'
    }
    return render(request, 'Admin_module/elections_list.html', context)


@login_required
@require_http_methods(["POST"])
def reset_user_password(request, user_id):
    """Reset a user's password to a randomly generated value"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied. Staff access required.'
        }, status=403)
    
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Generate a random secure password
        import string
        import secrets
        
        # Generate 12-character password with mix of letters, digits, and symbols
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Set the new password
        user.set_password(new_password)
        user.save()
        
        # Log the activity
        log_activity(
            user=request.user,
            action='admin_action',
            description=f'Reset password for user {user.username}',
            request=request,
            additional_data={
                'target_user': user.username,
                'target_user_id': user.id
            }
        )
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'new_password': new_password,
            'message': f'Password reset successfully for user {user.username}'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@require_http_methods(["POST"])
def user_delete(request):
    """Delete a user and their profile (POST-only, id from body)"""
    try:
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        username = user.username
        
        # Prevent deletion of superusers (safety measure)
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts')
            return redirect('admin_module:admin_dashboard')
        
        # Delete the user profile first (if it exists)
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_profile.delete()
        except UserProfile.DoesNotExist:
            pass  # Profile doesn't exist, continue with user deletion
        
        # Delete the user
        user.delete()
        
        # Log the activity
        log_activity(
            user=request.user,
            action='admin_action',
            description=f'Deleted user {username}',
            request=request
        )
        
        messages.success(request, f'User {username} has been deleted successfully')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
    
    return redirect('admin_module:admin_dashboard')


@staff_member_required
def course_analytics(request, election_id):
    """Show voting results grouped by course"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get votes grouped by course
    course_stats = []
    courses = Course.objects.all().order_by('department__name', 'name')
    
    total_votes = SchoolVote.objects.filter(election=election).count()
    
    for course in courses:
        course_votes = SchoolVote.objects.filter(
            election=election,
            voter__profile__course=course
        ).count()
        
        participation_rate = (course_votes / total_votes * 100) if total_votes > 0 else 0
        
        course_stats.append({
            'course': course,
            'vote_count': course_votes,
            'participation_rate': round(participation_rate, 1),
            'department': course.department
        })
    
    context = {
        'election': election,
        'course_stats': course_stats,
        'total_votes': total_votes,
        'page_title': f'Course Analytics: {election.title}'
    }
    return render(request, 'Admin_module/course_analytics.html', context)


@staff_member_required
def department_analytics(request, election_id):
    """Show voting results grouped by department"""
    election = get_object_or_404(SchoolElection, id=election_id)
    
    # Get votes grouped by department
    department_stats = []
    departments = Department.objects.all().order_by('name')
    
    total_votes = SchoolVote.objects.filter(election=election).count()
    
    for department in departments:
        dept_votes = SchoolVote.objects.filter(
            election=election,
            voter__profile__department=department
        ).count()
        
        participation_rate = (dept_votes / total_votes * 100) if total_votes > 0 else 0
        
        department_stats.append({
            'department': department,
            'vote_count': dept_votes,
            'participation_rate': round(participation_rate, 1),
            'courses_count': department.courses.count()
        })
    
    context = {
        'election': election,
        'department_stats': department_stats,
        'total_votes': total_votes,
        'page_title': f'Department Analytics: {election.title}'
    }
    return render(request, 'Admin_module/department_analytics.html', context)


# ============================================
# Department Management Views
# ============================================

@staff_member_required
def department_management(request):
    """Department management dashboard"""
    departments = Department.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'page_title': 'Department Management',
        'total_departments': Department.objects.count(),
        'total_courses': Course.objects.count(),
    }
    return render(request, 'Admin_module/department_management.html', context)


@staff_member_required
def department_create(request):
    """Create a new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Created department: {department.name} ({department.code})',
                request=request
            )
            
            messages.success(request, f'Department "{department.name}" created successfully!')
            return redirect('admin_module:department_management')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'page_title': 'Create Department'
    }
    return render(request, 'Admin_module/department_form.html', context)


@staff_member_required
def department_edit(request, department_id):
    """Edit an existing department"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Updated department: {department.name} ({department.code})',
                request=request
            )
            
            messages.success(request, f'Department "{department.name}" updated successfully!')
            return redirect('admin_module:department_management')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'page_title': f'Edit Department: {department.name}'
    }
    return render(request, 'Admin_module/department_form.html', context)


@staff_member_required
def department_delete(request):
    """Delete a department with options for handling connected courses (POST-only id)"""
    department_id = request.POST.get('department_id') or request.GET.get('department_id')
    department = get_object_or_404(Department, id=department_id)
    
    # Get courses in this department
    courses = department.courses.all()
    courses_count = courses.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_with_courses':
            # Delete department and all its courses
            department_name = department.name
            courses_deleted = courses_count
            
            # Delete all courses first
            for course in courses:
                course.delete()
            
            # Then delete the department
            department.delete()
            
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Deleted department "{department_name}" and {courses_deleted} associated courses',
                request=request
            )
            
            messages.success(request, f'Department "{department_name}" and {courses_deleted} course(s) deleted successfully!')
            
        elif action == 'reassign_courses':
            # Reassign courses to another department
            new_department_id = request.POST.get('new_department_id')
            if new_department_id:
                new_department = get_object_or_404(Department, id=new_department_id)
                department_name = department.name
                new_department_name = new_department.name
                
                # Update all courses to the new department
                courses.update(department=new_department)
                
                # Delete the old department
                department.delete()
                
                log_activity(
                    user=request.user,
                    action='admin_action',
                    description=f'Deleted department "{department_name}" and reassigned {courses_count} courses to "{new_department_name}"',
                    request=request
                )
                
                messages.success(request, f'Department "{department_name}" deleted successfully! {courses_count} course(s) reassigned to "{new_department_name}".')
            else:
                messages.error(request, 'Please select a department to reassign courses to.')
                return redirect('admin_module:department_delete', department_id=department_id)
        
        return redirect('admin_module:department_management')
    
    # Get all other departments for reassignment option
    other_departments = Department.objects.exclude(id=department.id).order_by('name')
    
    context = {
        'department': department,
        'courses': courses,
        'courses_count': courses_count,
        'other_departments': other_departments,
        'page_title': f'Delete Department: {department.name}'
    }
    return render(request, 'Admin_module/department_confirm_delete.html', context)


# ============================================
# Course Management Views
# ============================================

@staff_member_required
def course_management(request):
    """Course management dashboard"""
    courses = Course.objects.select_related('department').all().order_by('department__name', 'name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(department__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by department
    department_filter = request.GET.get('department', '')
    if department_filter:
        courses = courses.filter(department_id=department_filter)
    
    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'departments': Department.objects.all().order_by('name'),
        'page_title': 'Course Management',
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
    }
    return render(request, 'Admin_module/course_management.html', context)


@staff_member_required
def course_create(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Created course: {course.name} ({course.code}) in {course.department.name}',
                request=request
            )
            
            messages.success(request, f'Course "{course.name}" created successfully!')
            return redirect('admin_module:course_management')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
        'page_title': 'Create Course'
    }
    return render(request, 'Admin_module/course_form.html', context)


@staff_member_required
def course_edit(request, course_id):
    """Edit an existing course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Updated course: {course.name} ({course.code}) in {course.department.name}',
                request=request
            )
            
            messages.success(request, f'Course "{course.name}" updated successfully!')
            return redirect('admin_module:course_management')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course,
        'page_title': f'Edit Course: {course.name}'
    }
    return render(request, 'Admin_module/course_form.html', context)


@staff_member_required
def course_delete(request):
    """Delete a course (POST-only id)"""
    course_id = request.POST.get('course_id') or request.GET.get('course_id')
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        # Check if course has students before deleting
        students_count = course.students.count()
        if students_count > 0:
            messages.error(request, f'Cannot delete course "{course.name}" because it has {students_count} student(s) assigned to it.')
            return redirect('admin_module:course_management')
        
        course_name = course.name
        course.delete()
        
        log_activity(
            user=request.user,
            action='admin_action',
            description=f'Deleted course: {course_name}',
            request=request
        )
        
        messages.success(request, f'Course "{course_name}" deleted successfully!')
        return redirect('admin_module:course_management')
    
    # GET request - show confirmation page
    context = {
        'course': course,
        'page_title': f'Delete Course: {course.name}'
    }
    return render(request, 'Admin_module/course_confirm_delete.html', context)


# ============================================
# CSV Import/Export Views
# ============================================

@staff_member_required
def department_export_csv(request):
    """Export departments to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="departments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Code', 'Description', 'Courses Count'])
    
    departments = Department.objects.all().order_by('name')
    for department in departments:
        writer.writerow([
            department.name,
            department.code,
            department.description,
            department.courses.count()
        ])
    
    log_activity(
        user=request.user,
        action='admin_action',
        description='Exported departments to CSV',
        request=request
    )
    
    return response


@staff_member_required
def course_export_csv(request):
    """Export courses to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Code', 'Department', 'Department Code', 'Description', 'Students Count'])
    
    courses = Course.objects.select_related('department').all().order_by('department__name', 'name')
    for course in courses:
        writer.writerow([
            course.name,
            course.code,
            course.department.name,
            course.department.code,
            course.description,
            course.students.count()
        ])
    
    log_activity(
        user=request.user,
        action='admin_action',
        description='Exported courses to CSV',
        request=request
    )
    
    return response


@staff_member_required
def department_import_csv(request):
    """Import departments from CSV"""
    if request.method == 'POST':
        form = DepartmentCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')
                
                # Skip header row
                next(csv_data)
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_data, start=2):
                    if len(row) >= 3:  # name, code, description
                        name, code, description = row[0].strip(), row[1].strip(), row[2].strip()
                        
                        if name and code:
                            try:
                                department, created = Department.objects.get_or_create(
                                    code=code.upper(),
                                    defaults={
                                        'name': name,
                                        'description': description
                                    }
                                )
                                if created:
                                    imported_count += 1
                            except Exception as e:
                                errors.append(f'Row {row_num}: {str(e)}')
                        else:
                            errors.append(f'Row {row_num}: Missing name or code')
                    else:
                        errors.append(f'Row {row_num}: Insufficient columns')
                
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} department(s)!')
                
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        messages.error(request, error)
                    if len(errors) > 5:
                        messages.warning(request, f'... and {len(errors) - 5} more errors.')
                
                log_activity(
                    user=request.user,
                    action='admin_action',
                    description=f'Imported {imported_count} departments from CSV',
                    request=request
                )
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
            
            return redirect('admin_module:department_management')
    else:
        form = DepartmentCSVImportForm()
    
    context = {
        'form': form,
        'page_title': 'Import Departments from CSV'
    }
    return render(request, 'Admin_module/department_import_csv.html', context)


@staff_member_required
def course_import_csv(request):
    """Import courses from CSV"""
    if request.method == 'POST':
        form = CourseCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(decoded_file.splitlines(), delimiter=',')
                
                # Skip header row
                next(csv_data)
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_data, start=2):
                    if len(row) >= 4:  # name, code, department_code, description
                        name, code, dept_code, description = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
                        
                        if name and code and dept_code:
                            try:
                                department = Department.objects.get(code=dept_code.upper())
                                course, created = Course.objects.get_or_create(
                                    code=code.upper(),
                                    department=department,
                                    defaults={
                                        'name': name,
                                        'description': description
                                    }
                                )
                                if created:
                                    imported_count += 1
                            except Department.DoesNotExist:
                                errors.append(f'Row {row_num}: Department with code "{dept_code}" not found')
                            except Exception as e:
                                errors.append(f'Row {row_num}: {str(e)}')
                        else:
                            errors.append(f'Row {row_num}: Missing name, code, or department code')
                    else:
                        errors.append(f'Row {row_num}: Insufficient columns')
                
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} course(s)!')
                
                if errors:
                    for error in errors[:5]:  # Show first 5 errors
                        messages.error(request, error)
                    if len(errors) > 5:
                        messages.warning(request, f'... and {len(errors) - 5} more errors.')
                
                log_activity(
                    user=request.user,
                    action='admin_action',
                    description=f'Imported {imported_count} courses from CSV',
                    request=request
                )
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
            
            return redirect('admin_module:course_management')
    else:
        form = CourseCSVImportForm()
    
    context = {
        'form': form,
        'page_title': 'Import Courses from CSV'
    }
    return render(request, 'Admin_module/course_import_csv.html', context)


# ============================================
# Bulk User Generation Views

@staff_member_required
def bulk_user_generation(request):
    """Generate multiple random user accounts"""
    if request.method == 'POST':
        try:
            # Get form data
            count = int(request.POST.get('count', 10))
            department_id = request.POST.get('department_id')
            course_id = request.POST.get('course_id')
            year_level = request.POST.get('year_level', '1')
            password = request.POST.get('password', 'password123')
            randomize_year_level = request.POST.get('randomize_year_level') == '1'
            randomize_department = request.POST.get('randomize_department') == '1'
            randomize_course = request.POST.get('randomize_course') == '1'
            
            # Get year level distribution if randomization is enabled
            year_level_distribution = None
            if randomize_year_level:
                year_level_distribution = {
                    '1': int(request.POST.get('year1Range', 20)),
                    '2': int(request.POST.get('year2Range', 20)),
                    '3': int(request.POST.get('year3Range', 20)),
                    '4': int(request.POST.get('year4Range', 20)),
                    '5': int(request.POST.get('year5Range', 20))
                }
            
            # Get all departments and courses for randomization
            all_departments = list(Department.objects.filter(is_active=True))
            all_courses = list(Course.objects.filter(is_active=True))
            
            # Validate count
            if count < 1 or count > 100:
                messages.error(request, 'Count must be between 1 and 100.')
                return redirect('admin_module:bulk_user_generation')
            
            # Get department and course (either specific or random)
            department = None
            course = None
            
            if not randomize_department and department_id:
                department = get_object_or_404(Department, id=department_id)
            
            if not randomize_course and course_id:
                course = get_object_or_404(Course, id=course_id)
            
            # Function to select department (random or specific)
            def select_department():
                if randomize_department and all_departments:
                    return random.choice(all_departments)
                return department
            
            # Function to select course (random or specific)
            def select_course(selected_dept=None):
                if randomize_course and all_courses:
                    if selected_dept:
                        # Filter courses by selected department
                        dept_courses = [c for c in all_courses if c.department == selected_dept]
                        if dept_courses:
                            return random.choice(dept_courses)
                    # If no department-specific courses or no department, choose any course
                    return random.choice(all_courses)
                return course
            
            # Function to select year level based on distribution
            def select_year_level():
                if not randomize_year_level:
                    return year_level
                
                # Create weighted random selection
                rand_num = random.randint(1, 100)
                cumulative = 0
                
                for year, percentage in year_level_distribution.items():
                    cumulative += percentage
                    if rand_num <= cumulative:
                        return year
                
                return '1'  # Fallback
            
            # Generate users
            generated_users = []
            errors = []
            
            for i in range(count):
                try:
                    # Generate random user data
                    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica', 'Robert', 'Ashley', 'William', 'Amanda', 'Richard', 'Jennifer', 'Charles', 'Lisa', 'Joseph', 'Nancy', 'Thomas', 'Karen', 'Christopher', 'Betty', 'Daniel', 'Helen', 'Matthew', 'Sandra', 'Anthony', 'Donna', 'Mark', 'Carol', 'Donald', 'Ruth', 'Steven', 'Sharon', 'Paul', 'Michelle', 'Andrew', 'Laura', 'Joshua', 'Sarah', 'Kenneth', 'Kimberly', 'Kevin', 'Deborah', 'Brian', 'Dorothy', 'George', 'Lisa', 'Timothy', 'Nancy']
                    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts', 'Gomez']
                    
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
                    
                    # Ensure username is unique
                    counter = 1
                    original_username = username
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}{counter}"
                        counter += 1
                    
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=f"{username}@school.edu",
                        password=password
                    )
                    
                    # Create user profile
                    selected_year_level = select_year_level()
                    selected_department = select_department()
                    selected_course = select_course(selected_department)
                    
                    profile = UserProfile.objects.create(
                        user=user,
                        department=selected_department,
                        course=selected_course,
                        year_level=f"{selected_year_level}st Year" if selected_year_level == '1' else f"{selected_year_level}nd Year" if selected_year_level == '2' else f"{selected_year_level}rd Year" if selected_year_level == '3' else f"{selected_year_level}th Year",
                        is_verified=True
                    )
                    
                    generated_users.append({
                        'username': username,
                        'name': f"{first_name} {last_name}",
                        'student_id': profile.student_id,
                        'email': f"{username}@school.edu"
                    })
                    
                except Exception as e:
                    errors.append(f"Error creating user {i+1}: {str(e)}")
            
            # Log the activity
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Generated {len(generated_users)} bulk user accounts',
                request=request,
                additional_data={
                    'count': count,
                    'department': department.name if department else None,
                    'course': course.name if course else None,
                    'year_level': f"{year_level}st Year" if year_level == '1' else f"{year_level}nd Year" if year_level == '2' else f"{year_level}rd Year" if year_level == '3' else f"{year_level}th Year",
                    'randomize_department': randomize_department,
                    'randomize_course': randomize_course,
                    'randomize_year_level': randomize_year_level,
                    'year_level_distribution': year_level_distribution,
                    'generated_users': generated_users[:10]  # Log first 10 users
                }
            )
            
            # Show results
            if generated_users:
                messages.success(request, f'Successfully generated {len(generated_users)} user accounts!')
                request.session['generated_users'] = generated_users
                return redirect('admin_module:bulk_user_results')
            
            if errors:
                for error in errors[:5]:
                    messages.error(request, error)
                if len(errors) > 5:
                    messages.warning(request, f'... and {len(errors) - 5} more errors.')
            
        except Exception as e:
            messages.error(request, f'Error generating users: {str(e)}')
    
    # Get departments and courses for the form
    departments = Department.objects.filter(is_active=True).order_by('name')
    courses = Course.objects.filter(is_active=True).order_by('department__name', 'name')
    
    context = {
        'departments': departments,
        'courses': courses,
        'page_title': 'Bulk User Generation'
    }
    return render(request, 'Admin_module/bulk_user_generation.html', context)


@staff_member_required
def bulk_user_results(request):
    """Display results of bulk user generation"""
    generated_users = request.session.get('generated_users', [])
    
    if not generated_users:
        messages.warning(request, 'No generated users found. Please generate users first.')
        return redirect('admin_module:bulk_user_generation')
    
    # Clear the session data after displaying
    if 'generated_users' in request.session:
        del request.session['generated_users']
    
    context = {
        'generated_users': generated_users,
        'page_title': 'Bulk User Generation Results'
    }
    return render(request, 'Admin_module/bulk_user_results.html', context)


@staff_member_required
def user_autocomplete(request):
    """AJAX endpoint for user autocomplete search"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Annotate full name for more natural matching (e.g., "First Last")
    users_qs = (
        User.objects
        .annotate(full_name=Concat(F('first_name'), Value(' '), F('last_name')))
        .filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query)
        )
        .prefetch_related('profile__course', 'profile__department')
        .order_by('first_name', 'last_name')
    )

    # Limit results
    users = users_qs[:20]
    
    results = []
    for user in users:
        # Get user profile information if it exists
        profile = getattr(user, 'profile', None)
        if profile:
            student_id = profile.student_id if profile.student_id else ''
            year_level = profile.year_level if profile.year_level else ''
            course = profile.course.name if profile.course else 'N/A'
            
            # Build display text
            display_name = user.get_full_name() or user.username
            text = f"{display_name} ({user.username}) - {course}"
            if student_id:
                text = f"{display_name} ({student_id}) - {course}"
            
            results.append({
                'id': user.id,
                'text': text,
                'display_name': display_name,
                'username': user.username,
                'email': user.email,
                'student_id': student_id,
                'year_level': year_level,
                'course': course,
                'department': profile.department.name if profile.department else 'N/A'
            })
        else:
            # User without profile
            display_name = user.get_full_name() or user.username
            results.append({
                'id': user.id,
                'text': f"{display_name} ({user.username}) - No Profile",
                'display_name': display_name,
                'username': user.username,
                'email': user.email,
                'student_id': '',
                'year_level': '',
                'course': 'N/A',
                'department': 'N/A'
            })
    
    return JsonResponse({'results': results})


@staff_member_required
def user_detail(request, user_id):
    """Edit user details"""
    user_obj = get_object_or_404(User, id=user_id)
    user_profile, created = UserProfile.objects.get_or_create(user=user_obj)
    
    if request.method == 'POST':
        # Update user basic info
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.is_active = request.POST.get('is_active') == 'on'
        user_obj.is_staff = request.POST.get('is_staff') == 'on'
        user_obj.is_superuser = request.POST.get('is_superuser') == 'on'
        user_obj.save()
        
        # Update profile
        user_profile.student_id = request.POST.get('student_id', '')
        user_profile.year_level = request.POST.get('year_level', '')
        
        # Handle verification status change
        old_verified_status = user_profile.is_verified
        user_profile.is_verified = request.POST.get('is_verified') == 'on'
        
        # Auto-generate student ID when user gets verified
        if not old_verified_status and user_profile.is_verified and not user_profile.student_id:
            current_year = timezone.now().year
            import random
            random_num = random.randint(10000, 99999)
            user_profile.student_id = f"{current_year}-{random_num}"
            
            # Log the auto-generation
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Auto-generated student ID {user_profile.student_id} for user {user_obj.username} upon verification',
                request=request,
                additional_data={
                    'target_user': user_obj.username,
                    'student_id': user_profile.student_id,
                    'action': 'auto_generated_student_id'
                }
            )
        
        # Update department
        dept_id = request.POST.get('department')
        if dept_id:
            try:
                user_profile.department = Department.objects.get(id=dept_id)
            except Department.DoesNotExist:
                pass
        else:
            user_profile.department = None
        
        # Update course
        course_id = request.POST.get('course')
        if course_id:
            try:
                user_profile.course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                pass
        else:
            user_profile.course = None
        
        user_profile.save()
        
        # Log the user update
        log_activity(
            user=request.user,
            action='admin_action',
            description=f'Updated user profile for {user_obj.username}',
            request=request,
            additional_data={
                'target_user': user_obj.username,
                'changes': {
                    'first_name': user_obj.first_name,
                    'last_name': user_obj.last_name,
                    'email': user_obj.email,
                    'is_active': user_obj.is_active,
                    'is_staff': user_obj.is_staff,
                    'is_superuser': user_obj.is_superuser,
                    'is_verified': user_profile.is_verified,
                    'student_id': user_profile.student_id,
                    'department': user_profile.department.name if user_profile.department else None,
                    'course': user_profile.course.name if user_profile.course else None,
                    'year_level': user_profile.year_level
                }
            }
        )
        
        messages.success(request, f'User {user_obj.username} updated successfully!')
        return redirect('admin_module:admin_dashboard')
    
    # Get departments and courses for the form
    departments = Department.objects.filter(is_active=True).order_by('name')
    courses = Course.objects.filter(is_active=True).order_by('department__name', 'name')
    
    context = {
        'user_obj': user_obj,
        'profile': user_profile,
        'departments': departments,
        'courses': courses,
        'page_title': f'Edit User - {user_obj.username}'
    }
    return render(request, 'Admin_module/user_detail.html', context)


@login_required
@require_http_methods(["POST"])
def user_edit_ajax(request):
    """AJAX endpoint for editing user details"""
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied. Staff access required.'
        }, status=403)
    
    try:
        user_id = request.POST.get('user_id')
        user_obj = get_object_or_404(User, id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=user_obj)
        
        # Update user basic info
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.is_active = request.POST.get('is_active') == 'on'
        user_obj.is_staff = request.POST.get('is_staff') == 'on'
        user_obj.is_superuser = request.POST.get('is_superuser') == 'on'
        user_obj.save()
        
        # Update profile
        user_profile.student_id = request.POST.get('student_id', '')
        user_profile.year_level = request.POST.get('year_level', '')
        
        # Handle verification status change
        old_verified_status = user_profile.is_verified
        user_profile.is_verified = request.POST.get('is_verified') == 'on'
        
        # Auto-generate student ID when user gets verified
        if not old_verified_status and user_profile.is_verified and not user_profile.student_id:
            current_year = timezone.now().year
            random_num = random.randint(10000, 99999)
            user_profile.student_id = f"{current_year}-{random_num}"
            
            # Log the auto-generation
            log_activity(
                user=request.user,
                action='admin_action',
                description=f'Auto-generated student ID {user_profile.student_id} for user {user_obj.username} upon verification',
                request=request,
                additional_data={
                    'target_user': user_obj.username,
                    'student_id': user_profile.student_id,
                    'action': 'auto_generated_student_id'
                }
            )
        
        # Update course
        course_id = request.POST.get('course')
        if course_id:
            try:
                user_profile.course = Course.objects.get(id=course_id)
                # Auto-set department from course
                if user_profile.course:
                    user_profile.department = user_profile.course.department
            except Course.DoesNotExist:
                pass
        else:
            user_profile.course = None
            user_profile.department = None
        
        user_profile.save()
        
        # Log the user update
        log_activity(
            user=request.user,
            action='admin_action',
            description=f'Updated user profile for {user_obj.username} via AJAX',
            request=request,
            additional_data={
                'target_user': user_obj.username,
                'changes': {
                    'first_name': user_obj.first_name,
                    'last_name': user_obj.last_name,
                    'email': user_obj.email,
                    'is_active': user_obj.is_active,
                    'is_staff': user_obj.is_staff,
                    'is_superuser': user_obj.is_superuser,
                    'is_verified': user_profile.is_verified,
                    'student_id': user_profile.student_id,
                    'department': user_profile.department.name if user_profile.department else None,
                    'course': user_profile.course.name if user_profile.course else None,
                    'year_level': user_profile.year_level
                }
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'User {user_obj.username} updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })