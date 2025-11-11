"""
Consolidated validation utilities for E-Botar system
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class StudentIDValidator(RegexValidator):
    """Validator for student ID format (XXXX-XXXXX)"""
    regex = r'^\d{4}-\d{5}$'
    message = _('Student ID must be in format XXXX-XXXXX (e.g., 2024-12345)')
    code = 'invalid_student_id'


def validate_student_id(value):
    """Validate student ID format"""
    validator = StudentIDValidator()
    validator(value)


def validate_email_domain(email, allowed_domains=None):
    """Validate email domain"""
    if allowed_domains is None:
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    
    domain = email.split('@')[1].lower()
    if domain not in allowed_domains:
        raise ValidationError(f"Email domain '{domain}' is not allowed")


def validate_phone_number(phone_number):
    """Validate Philippine phone number format"""
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', phone_number)
    
    # Check if it starts with 09 and has 11 digits
    if not re.match(r'^09\d{9}$', cleaned):
        raise ValidationError("Phone number must be in format 09XXXXXXXXX (11 digits starting with 09)")
    
    return cleaned


def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character")


def validate_year_level(year_level):
    """Validate year level format"""
    valid_levels = ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year']
    if year_level not in valid_levels:
        raise ValidationError(f"Year level must be one of: {', '.join(valid_levels)}")


def validate_election_dates(start_date, end_date):
    """Validate election date range"""
    if start_date >= end_date:
        raise ValidationError("End date must be after start date")
    
    from django.utils import timezone
    if start_date < timezone.now():
        raise ValidationError("Start date cannot be in the past")


def validate_candidate_application(user, election, position):
    """Validate candidate application"""
    from candidate_module.models import CandidateApplication
    
    # Check if user already applied for this position in this election
    existing = CandidateApplication.objects.filter(
        user=user,
        election=election,
        position=position
    ).exists()
    
    if existing:
        raise ValidationError("You have already applied for this position in this election")
    
    # Check if user is already a candidate for this position
    from candidate_module.models import Candidate
    existing_candidate = Candidate.objects.filter(
        user=user,
        election=election,
        position=position
    ).exists()
    
    if existing_candidate:
        raise ValidationError("You are already a candidate for this position")


def validate_vote_casting(user, election, position):
    """Validate vote casting"""
    from voting_module.models import SchoolVote
    
    # Check if user already voted for this position
    existing_vote = SchoolVote.objects.filter(
        voter=user,
        election=election,
        position=position
    ).exists()
    
    if existing_vote:
        raise ValidationError("You have already voted for this position")
    
    # Check if election is active
    if not election.is_active:
        raise ValidationError("This election is not currently active")
    
    # Check if election is within voting period
    from django.utils import timezone
    now = timezone.now()
    if now < election.start_date:
        raise ValidationError("Voting has not started yet")
    if now > election.end_date:
        raise ValidationError("Voting has ended")


def validate_file_upload(file, allowed_types=None, max_size=None):
    """Validate file upload"""
    if allowed_types is None:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    
    if max_size is None:
        max_size = 5 * 1024 * 1024  # 5MB
    
    # Check file type
    if file.content_type not in allowed_types:
        raise ValidationError(f"File type {file.content_type} is not allowed")
    
    # Check file size
    if file.size > max_size:
        raise ValidationError(f"File size {file.size} exceeds maximum {max_size}")
    
    return True


def validate_manifesto_length(manifesto):
    """Validate manifesto length"""
    if len(manifesto) < 50:
        raise ValidationError("Manifesto must be at least 50 characters long")
    
    if len(manifesto) > 2000:
        raise ValidationError("Manifesto must not exceed 2000 characters")


def validate_party_name(party_name):
    """Validate party name"""
    if len(party_name) < 3:
        raise ValidationError("Party name must be at least 3 characters long")
    
    if len(party_name) > 100:
        raise ValidationError("Party name must not exceed 100 characters")
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\s\-&.,()]+$', party_name):
        raise ValidationError("Party name contains invalid characters")


def validate_election_title(title):
    """Validate election title"""
    if len(title) < 5:
        raise ValidationError("Election title must be at least 5 characters long")
    
    if len(title) > 200:
        raise ValidationError("Election title must not exceed 200 characters")


def validate_position_name(name):
    """Validate position name"""
    if len(name) < 3:
        raise ValidationError("Position name must be at least 3 characters long")
    
    if len(name) > 100:
        raise ValidationError("Position name must not exceed 100 characters")


def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_csv_data(data, required_fields=None):
    """Validate CSV data structure"""
    if required_fields is None:
        required_fields = ['username', 'email', 'first_name', 'last_name']
    
    if not data:
        raise ValidationError("No data provided")
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in data[0]:
            raise ValidationError(f"Required field '{field}' is missing")
    
    return True
