"""
System constants for E-Botar voting system
"""

# User Roles
USER_ROLES = {
    'STUDENT': 'student',
    'ADMIN': 'admin',
    'SUPERUSER': 'superuser',
}

# Activity Types
ACTIVITY_TYPES = [
    ('login', 'User Login'),
    ('logout', 'User Logout'),
    ('register', 'User Registration'),
    ('vote', 'Vote Cast'),
    ('timeout', 'User Timeout'),
    ('create_poll', 'Poll Created'),
    ('create_election', 'Election Created'),
    ('create_candidate', 'Candidate Created'),
    ('update_profile', 'Profile Updated'),
    ('admin_action', 'Admin Action'),
    ('system_action', 'System Action'),
    ('error', 'Error Occurred'),
]

# Election Status
ELECTION_STATUS = {
    'UPCOMING': 'upcoming',
    'ACTIVE': 'active',
    'ENDED': 'ended',
}

# Candidate Application Status
CANDIDATE_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

# Vote Status
VOTE_STATUS = {
    'CAST': 'cast',
    'PENDING': 'pending',
    'INVALID': 'invalid',
}

# File Upload Limits
FILE_LIMITS = {
    'MAX_IMAGE_SIZE': 5 * 1024 * 1024,  # 5MB
    'MAX_DOCUMENT_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_IMAGE_TYPES': ['image/jpeg', 'image/png', 'image/gif'],
    'ALLOWED_DOCUMENT_TYPES': ['application/pdf', 'text/csv', 'application/vnd.ms-excel'],
}

# Validation Patterns
VALIDATION_PATTERNS = {
    'STUDENT_ID': r'^\d{4}-\d{5}$',
    'PHONE_NUMBER': r'^09\d{9}$',
    'EMAIL': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}

# Pagination
PAGINATION = {
    'DEFAULT_PER_PAGE': 20,
    'MAX_PER_PAGE': 100,
    'ADMIN_PER_PAGE': 50,
}

# Security Settings
SECURITY = {
    'SESSION_TIMEOUT': 30 * 60,  # 30 minutes
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 15 * 60,  # 15 minutes
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_REQUIREMENTS': {
        'UPPERCASE': True,
        'LOWERCASE': True,
        'DIGITS': True,
        'SPECIAL_CHARS': True,
    }
}

# Email Settings
EMAIL_SETTINGS = {
    'WELCOME_SUBJECT': 'Welcome to E-Botar Voting System',
    'PASSWORD_RESET_SUBJECT': 'Password Reset - E-Botar Voting System',
    'ELECTION_NOTIFICATION_SUBJECT': 'Election Notification - E-Botar',
    'VOTE_RECEIPT_SUBJECT': 'Vote Receipt - E-Botar Voting System',
}

# UI Settings
UI_SETTINGS = {
    'THEME_COLORS': {
        'PRIMARY': '#28a745',
        'SECONDARY': '#ffc107',
        'SUCCESS': '#28a745',
        'DANGER': '#dc3545',
        'WARNING': '#ffc107',
        'INFO': '#17a2b8',
    },
    'CHART_COLORS': [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
    ],
}

# Academic Structure
ACADEMIC_STRUCTURE = {
    'YEAR_LEVELS': [
        '1st Year',
        '2nd Year', 
        '3rd Year',
        '4th Year',
        '5th Year'
    ],
    'DEFAULT_DEPARTMENTS': [
        {'name': 'Computer Science', 'code': 'CS'},
        {'name': 'Engineering', 'code': 'ENG'},
        {'name': 'Business Administration', 'code': 'BA'},
        {'name': 'Education', 'code': 'EDU'},
    ]
}

# Election Settings
ELECTION_SETTINGS = {
    'MIN_DURATION_HOURS': 1,
    'MAX_DURATION_DAYS': 30,
    'DEFAULT_DURATION_DAYS': 7,
    'MIN_CANDIDATES_PER_POSITION': 2,
    'MAX_CANDIDATES_PER_POSITION': 10,
}

# Voting Settings
VOTING_SETTINGS = {
    'ALLOW_EARLY_VOTING': False,
    'ALLOW_LATE_VOTING': False,
    'REQUIRE_VERIFICATION': True,
    'ANONYMIZE_VOTES': True,
    'GENERATE_RECEIPTS': True,
}

# System Messages
SYSTEM_MESSAGES = {
    'VOTE_SUCCESS': 'Your vote has been cast successfully!',
    'VOTE_ALREADY_CAST': 'You have already voted for this position.',
    'ELECTION_NOT_ACTIVE': 'This election is not currently active.',
    'VOTING_ENDED': 'Voting has ended for this election.',
    'VOTING_NOT_STARTED': 'Voting has not started yet.',
    'CANDIDATE_APPLICATION_SUCCESS': 'Your candidate application has been submitted successfully!',
    'CANDIDATE_ALREADY_APPLIED': 'You have already applied for this position.',
    'PROFILE_UPDATED': 'Your profile has been updated successfully!',
    'PASSWORD_CHANGED': 'Your password has been changed successfully!',
}

# Error Messages
ERROR_MESSAGES = {
    'INVALID_STUDENT_ID': 'Student ID must be in format XXXX-XXXXX (e.g., 2024-12345)',
    'INVALID_PHONE_NUMBER': 'Phone number must be in format 09XXXXXXXXX (11 digits starting with 09)',
    'INVALID_EMAIL': 'Please enter a valid email address',
    'PASSWORD_TOO_WEAK': 'Password does not meet security requirements',
    'FILE_TOO_LARGE': 'File size exceeds the maximum allowed limit',
    'INVALID_FILE_TYPE': 'File type is not allowed',
    'REQUIRED_FIELD': 'This field is required',
    'UNIQUE_CONSTRAINT': 'This value already exists',
}

# API Response Codes
API_CODES = {
    'SUCCESS': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': 405,
    'CONFLICT': 409,
    'INTERNAL_ERROR': 500,
}

# Database Settings
DATABASE_SETTINGS = {
    'BATCH_SIZE': 1000,
    'QUERY_TIMEOUT': 30,
    'MAX_CONNECTIONS': 20,
}

# Cache Settings
CACHE_SETTINGS = {
    'DEFAULT_TIMEOUT': 300,  # 5 minutes
    'ELECTION_RESULTS_TIMEOUT': 60,  # 1 minute
    'USER_SESSION_TIMEOUT': 1800,  # 30 minutes
}

# Logging Settings
LOGGING_SETTINGS = {
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_FILE_MAX_SIZE': 10 * 1024 * 1024,  # 10MB
    'LOG_FILE_BACKUP_COUNT': 5,
}

# Feature Flags
FEATURE_FLAGS = {
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'ENABLE_SMS_NOTIFICATIONS': False,
    'ENABLE_TWO_FACTOR_AUTH': False,
    'ENABLE_API_ACCESS': True,
    'ENABLE_BULK_OPERATIONS': True,
    'ENABLE_DATA_EXPORT': True,
    'ENABLE_ADVANCED_ANALYTICS': True,
}
