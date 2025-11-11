#!/usr/bin/env python
"""
Candidate Application Validation and Cleanup Script

This script validates candidate applications against business rules and
cleans up any invalid or problematic data.

Usage:
    python manage.py shell -c "exec(open('scripts/validate_candidate_applications.py').read())"
"""

import os
import sys

from candidate_module.models import CandidateApplication, Candidate
from election_module.models import SchoolElection, SchoolPosition
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count


def validate_candidate_applications():
    """Validate all candidate applications and report issues"""
    print("=== CANDIDATE APPLICATION VALIDATION ===")
    
    applications = CandidateApplication.objects.all()
    print(f"Total applications found: {applications.count()}")
    
    issues = []
    valid_apps = []
    
    for app in applications:
        app_issues = []
        
        # Check basic data integrity
        if not app.user:
            app_issues.append("Missing user")
        elif not app.user.is_active:
            app_issues.append("User is inactive")
        elif app.user.is_superuser:
            app_issues.append("Admin user should not be a candidate")
            
        if not app.position:
            app_issues.append("Missing position")
        elif not app.position.is_active:
            app_issues.append("Position is inactive")
            
        if not app.election:
            app_issues.append("Missing election")
        elif not app.election.is_active:
            app_issues.append("Election is inactive")
            
        if not app.manifesto or app.manifesto.strip() == "":
            app_issues.append("Missing or empty manifesto")
            
        # Check business rules using model validation
        try:
            app.clean()
        except ValidationError as e:
            app_issues.append(f"Business rule violation: {e}")
        except Exception as e:
            app_issues.append(f"Validation error: {e}")
            
        if app_issues:
            issues.append((app, app_issues))
        else:
            valid_apps.append(app)
    
    return valid_apps, issues


def check_duplicate_applications():
    """Check for duplicate applications"""
    print("\n=== DUPLICATE APPLICATION CHECK ===")
    
    duplicates = CandidateApplication.objects.values(
        'user', 'position', 'election'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates.count() > 0:
        print(f"Found {duplicates.count()} duplicate application groups:")
        for dup in duplicates:
            apps = CandidateApplication.objects.filter(
                user_id=dup['user'],
                position_id=dup['position'],
                election_id=dup['election']
            )
            print(f"  User {dup['user']}, Position {dup['position']}, Election {dup['election']}:")
            for app in apps:
                print(f"    - ID {app.id}: Status {app.status}, Submitted {app.submitted_at}")
        return True
    else:
        print("No duplicate applications found")
        return False


def cleanup_invalid_applications(issues):
    """Clean up invalid applications"""
    print("\n=== CLEANUP OPERATIONS ===")
    
    removed_count = 0
    
    for app, app_issues in issues:
        should_remove = False
        reason = ""
        
        # Remove admin applications
        if "Admin user should not be a candidate" in app_issues:
            should_remove = True
            reason = "Admin user application"
            
        # Remove applications with inactive users
        elif "User is inactive" in app_issues:
            should_remove = True
            reason = "Inactive user application"
            
        # Remove applications with missing critical data
        elif "Missing user" in app_issues or "Missing position" in app_issues or "Missing election" in app_issues:
            should_remove = True
            reason = "Missing critical data"
            
        if should_remove:
            print(f"Removing application ID {app.id}: {app.user.get_full_name() if app.user else 'Unknown'} - {reason}")
            app.delete()
            removed_count += 1
    
    print(f"Removed {removed_count} invalid applications")
    return removed_count


def fix_user_profiles():
    """Fix user profiles that are missing names"""
    print("\n=== USER PROFILE FIXES ===")
    
    fixed_count = 0
    
    # Fix admin users
    admin_users = User.objects.filter(is_superuser=True, first_name='')
    for user in admin_users:
        user.first_name = 'System'
        user.last_name = 'Administrator'
        user.save()
        print(f"Fixed admin user profile: {user.username}")
        fixed_count += 1
    
    # Fix users with empty names
    users_without_names = User.objects.filter(first_name='', last_name='')
    for user in users_without_names:
        if not user.is_superuser:  # Don't override admin users we just fixed
            user.first_name = user.username.title()
            user.last_name = 'User'
            user.save()
            print(f"Fixed user profile: {user.username}")
            fixed_count += 1
    
    print(f"Fixed {fixed_count} user profiles")
    return fixed_count


def main():
    """Main validation and cleanup process"""
    print("Starting candidate application validation and cleanup...")
    
    # Validate applications
    valid_apps, issues = validate_candidate_applications()
    
    print(f"\n=== VALIDATION RESULTS ===")
    print(f"Valid applications: {len(valid_apps)}")
    print(f"Applications with issues: {len(issues)}")
    
    if issues:
        print("\nIssues found:")
        for app, app_issues in issues:
            print(f"  Application ID {app.id} ({app.user.get_full_name() if app.user else 'Unknown'}):")
            for issue in app_issues:
                print(f"    - {issue}")
    
    # Check for duplicates
    has_duplicates = check_duplicate_applications()
    
    # Clean up invalid applications
    removed_count = cleanup_invalid_applications(issues)
    
    # Fix user profiles
    fixed_profiles = fix_user_profiles()
    
    # Final summary
    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"Removed invalid applications: {removed_count}")
    print(f"Fixed user profiles: {fixed_profiles}")
    print(f"Duplicate applications found: {'Yes' if has_duplicates else 'No'}")
    
    # Show final state
    remaining_apps = CandidateApplication.objects.all()
    print(f"\n=== FINAL STATE ===")
    print(f"Remaining applications: {remaining_apps.count()}")
    for app in remaining_apps:
        print(f"  - ID {app.id}: {app.user.get_full_name()} - {app.position.name} - {app.status}")
    
    print("\nValidation and cleanup completed!")


if __name__ == "__main__":
    main()
