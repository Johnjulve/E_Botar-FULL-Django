"""
Consolidated helper utilities for E-Botar system
"""
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)


def get_paginated_data(queryset, page_number=1, per_page=20):
    """Get paginated data from queryset"""
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    
    return {
        'data': list(page_obj.object_list),
        'page_number': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_count': paginator.count
    }


def search_users(query, filters=None):
    """Search users with filters"""
    queryset = User.objects.select_related('userprofile', 'userprofile__department', 'userprofile__course')
    
    if query:
        queryset = queryset.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(userprofile__student_id__icontains=query)
        )
    
    if filters:
        if filters.get('department'):
            queryset = queryset.filter(userprofile__department__id=filters['department'])
        
        if filters.get('course'):
            queryset = queryset.filter(userprofile__course__id=filters['course'])
        
        if filters.get('year_level'):
            queryset = queryset.filter(userprofile__year_level=filters['year_level'])
        
        if filters.get('is_verified') is not None:
            queryset = queryset.filter(userprofile__is_verified=filters['is_verified'])
        
        if filters.get('is_active') is not None:
            queryset = queryset.filter(is_active=filters['is_active'])
    
    return queryset


def format_datetime(dt, format_string='%Y-%m-%d %H:%M:%S'):
    """Format datetime for display"""
    if dt is None:
        return '-'
    
    if isinstance(dt, str):
        return dt
    
    return dt.strftime(format_string)


def get_time_remaining(start_date, end_date):
    """Get time remaining between two dates"""
    now = timezone.now()
    
    if now < start_date:
        delta = start_date - now
        return f"Starts in {delta.days} days, {delta.seconds // 3600} hours"
    elif now < end_date:
        delta = end_date - now
        return f"Ends in {delta.days} days, {delta.seconds // 3600} hours"
    else:
        return "Ended"


def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def generate_unique_code(prefix='', length=8):
    """Generate unique code"""
    import uuid
    import random
    import string
    
    if prefix:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        return f"{prefix}-{random_part}"
    else:
        return str(uuid.uuid4())[:length].upper()


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent string"""
    return request.META.get('HTTP_USER_AGENT', '')


def is_ajax(request):
    """Check if request is AJAX"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def json_response(data, status=200):
    """Create JSON response"""
    return JsonResponse(data, status=status, encoder=DjangoJSONEncoder)


def safe_json_loads(json_string):
    """Safely load JSON string"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_json_dumps(data):
    """Safely dump data to JSON string"""
    try:
        return json.dumps(data, cls=DjangoJSONEncoder)
    except (TypeError, ValueError):
        return None


def get_school_year():
    """Get current school year"""
    now = timezone.now()
    year = now.year
    
    # Assume school year starts in June
    if now.month >= 6:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"


def format_student_id(student_id):
    """Format student ID for display"""
    if not student_id:
        return '-'
    
    # Remove any non-digit characters except dash
    cleaned = ''.join(c for c in student_id if c.isdigit() or c == '-')
    
    # Ensure proper format
    if len(cleaned) == 9 and '-' in cleaned:
        return cleaned
    elif len(cleaned) == 9:
        return f"{cleaned[:4]}-{cleaned[4:]}"
    else:
        return student_id


def get_election_status(election):
    """Get election status"""
    now = timezone.now()
    
    if now < election.start_date:
        return 'upcoming'
    elif now >= election.start_date and now <= election.end_date:
        return 'active'
    else:
        return 'ended'


def get_voting_statistics(election):
    """Get voting statistics for election"""
    from voting_module.models import SchoolVote
    from auth_module.models import UserProfile
    
    total_eligible_voters = UserProfile.objects.count()
    total_votes_cast = SchoolVote.objects.filter(election=election).count()
    participation_rate = calculate_percentage(total_votes_cast, total_eligible_voters)
    
    return {
        'total_eligible_voters': total_eligible_voters,
        'total_votes_cast': total_votes_cast,
        'participation_rate': participation_rate,
        'remaining_voters': total_eligible_voters - total_votes_cast
    }


def export_data_to_csv(data, filename):
    """Export data to CSV file"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if data:
        # Write header
        writer.writerow(data[0].keys())
        
        # Write data
        for row in data:
            writer.writerow(row.values())
    
    return output.getvalue()


def import_data_from_csv(csv_data):
    """Import data from CSV string"""
    import csv
    import io
    
    reader = csv.DictReader(io.StringIO(csv_data))
    return list(reader)


def clean_filename(filename):
    """Clean filename for safe storage"""
    import re
    
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = re.sub(r'\.+', '.', cleaned)
    
    return cleaned


def get_file_size_display(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to specified length"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_random_color():
    """Get random color for UI elements"""
    import random
    
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
    ]
    
    return random.choice(colors)


def format_phone_number(phone_number):
    """Format phone number for display"""
    if not phone_number:
        return '-'
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone_number))
    
    # Format as 09XX XXX XXXX
    if len(digits) == 11 and digits.startswith('09'):
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
    
    return phone_number
