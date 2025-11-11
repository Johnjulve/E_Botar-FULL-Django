from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import re

from .models import UserProfile, Department, Course


def register_view(request: HttpRequest) -> HttpResponse:
    """Register page for new users"""
    if request.user.is_authenticated:
        return redirect('home')
    
    error = None
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password1 = request.POST.get('password1') or ''
        password2 = request.POST.get('password2') or ''
        
        # Validation
        if not username or len(username) < 3:
            error = 'Username must be at least 3 characters long.'
        elif not email or '@' not in email:
            error = 'Please enter a valid email address.'
        elif not password1 or len(password1) < 8:
            error = 'Password must be at least 8 characters long.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        elif User.objects.filter(email=email).exists():
            error = 'Email already registered.'
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('auth_module:login')
    
    return render(request, 'Auth_module/register.html', {'error': error})


def login_view(request: HttpRequest) -> HttpResponse:
    """Login page using Template/Users/login.html.
    Accepts "username" and "password" fields from the template.
    """
    if request.user.is_authenticated:
        return redirect('home')
    error = None
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        error = 'Invalid username or password.'
    return render(request, 'Auth_module/login.html', {'error': error})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Logout view that logs out the user and redirects to home"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been logged out successfully, {username}.')
    else:
        messages.info(request, 'You were not logged in.')
    
    return redirect('home')


@login_required
def profile_view(request):
    """User profile management page"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    
    departments = Department.objects.all()
    
    # Only show courses from the selected department initially
    if user_profile.department:
        available_courses = Course.objects.filter(department=user_profile.department).order_by('name')
    else:
        available_courses = Course.objects.none()
    
    # Store the uploaded file temporarily if it exists
    has_validation_error = False
    
    if request.method == 'POST':
        # Handle password change first (separate from profile update)
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password or new_password or confirm_password:
            if current_password and new_password and confirm_password:
                if new_password == confirm_password:
                    if request.user.check_password(current_password):
                        request.user.set_password(new_password)
                        request.user.save()
                        update_session_auth_hash(request, request.user)
                        messages.success(request, 'Password changed successfully!')
                    else:
                        messages.error(request, 'Current password is incorrect.')
                        has_validation_error = True
                else:
                    messages.error(request, 'New passwords do not match.')
                    has_validation_error = True
            else:
                messages.error(request, 'Please fill in all password fields to change your password.')
                has_validation_error = True
        
        # Handle username change
        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != request.user.username:
            # Check if username is already taken
            if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                messages.error(request, 'Username is already taken. Please choose a different one.')
                has_validation_error = True
            elif len(new_username) < 3:
                messages.error(request, 'Username must be at least 3 characters long.')
                has_validation_error = True
            elif not re.match(r'^[a-zA-Z0-9._-]+$', new_username):
                messages.error(request, 'Username can only contain letters, numbers, dots, underscores, and hyphens.')
                has_validation_error = True
            else:
                # Log the username change
                from E_Botar.utils.logging_utils import log_activity
                log_activity(
                    user=request.user,
                    action='username_changed',
                    description=f'Changed username from "{request.user.username}" to "{new_username}"',
                    request=request,
                    additional_data={
                        'old_username': request.user.username,
                        'new_username': new_username
                    }
                )
                request.user.username = new_username
        
        # Update user basic info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        
        # Only save user if no validation errors
        if not has_validation_error:
            request.user.save()
        
        # Handle profile updates
        # Only allow staff to change student_id, regular users cannot modify it
        if request.user.is_staff:
            user_profile.student_id = request.POST.get('student_id', '')
        else:
            # For regular users, only auto-generate if they don't have one and are verified
            if not user_profile.student_id and user_profile.is_verified:
                # Auto-generate student ID for verified users
                current_year = timezone.now().year
                import random
                random_num = random.randint(10000, 99999)
                user_profile.student_id = f"{current_year}-{random_num}"
        
        # Update department
        dept_id = request.POST.get('department')
        if dept_id:
            try:
                new_department = Department.objects.get(id=dept_id)
                user_profile.department = new_department
                
                # If user has a course selected, check if it belongs to the new department
                if user_profile.course and user_profile.course.department != new_department:
                    user_profile.course = None  # Clear course if it doesn't belong to new department
            except Department.DoesNotExist:
                pass
        else:
            user_profile.department = None
            user_profile.course = None  # Clear course if no department selected
        
        # Update course
        course_id = request.POST.get('course')
        if course_id:
            try:
                user_profile.course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                pass
        
        user_profile.year_level = request.POST.get('year_level', '')
        
        # Handle avatar upload - save immediately to prevent loss
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
            # Save the profile immediately to persist the file
            user_profile.save()
        
        # Only save profile and show success message if no validation errors
        if not has_validation_error:
            user_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('auth_module:profile')
    
    context = {
        'user_obj': request.user,
        'profile': user_profile,
        'departments': departments,
        'available_courses': available_courses,
        'page_title': 'My Profile'
    }
    return render(request, 'Auth_module/profile.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def get_courses_by_department(request, department_id):
    """AJAX endpoint to get courses by department"""
    try:
        department = Department.objects.get(id=department_id)
        courses = Course.objects.filter(department=department).order_by('name')
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'code': course.code
            })
        
        return JsonResponse({
            'success': True,
            'courses': courses_data
        })
    except Department.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Department not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def generate_student_id(request):
    """AJAX endpoint to generate a new student ID"""
    try:
        # Generate a new student ID
        student_id = UserProfile.generate_student_id()
        
        return JsonResponse({
            'success': True,
            'student_id': student_id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
