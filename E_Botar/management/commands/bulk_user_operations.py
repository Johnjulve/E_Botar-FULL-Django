from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth_module.models import UserProfile, Department, Course
from django.db import transaction
import csv
import io


class Command(BaseCommand):
    help = 'Bulk user operations - import/export users from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--import', type=str, help='Import users from CSV file')
        parser.add_argument('--export', type=str, help='Export users to CSV file')
        parser.add_argument('--template', action='store_true', help='Generate CSV template')

    def handle(self, *args, **options):
        if options['template']:
            self.generate_template()
        elif options['import']:
            self.import_users(options['import'])
        elif options['export']:
            self.export_users(options['export'])
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify an action:\n'
                    '  --template: Generate CSV template\n'
                    '  --import <file>: Import users from CSV\n'
                    '  --export <file>: Export users to CSV'
                )
            )

    def generate_template(self):
        """Generate a CSV template for user import"""
        template_data = [
            ['username', 'email', 'first_name', 'last_name', 'student_id', 'department_code', 'course_code', 'year_level', 'phone_number'],
            ['john.doe', 'john.doe@example.com', 'John', 'Doe', '2024-12345', 'CS', 'BSCS', '2nd Year', '09123456789'],
            ['jane.smith', 'jane.smith@example.com', 'Jane', 'Smith', '2024-12346', 'ENG', 'BSCE', '3rd Year', '09123456790'],
        ]
        
        filename = 'user_import_template.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(template_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'CSV template generated: {filename}')
        )

    def import_users(self, filename):
        """Import users from CSV file"""
        self.stdout.write(f'Importing users from {filename}...')
        
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                imported_count = 0
                error_count = 0
                
                with transaction.atomic():
                    for row in reader:
                        try:
                            # Get or create department
                            department = None
                            if row.get('department_code'):
                                department = Department.objects.get(code=row['department_code'])
                            
                            # Get or create course
                            course = None
                            if row.get('course_code') and department:
                                course = Course.objects.get(
                                    code=row['course_code'],
                                    department=department
                                )
                            
                            # Create user
                            user, created = User.objects.get_or_create(
                                username=row['username'],
                                defaults={
                                    'email': row['email'],
                                    'first_name': row['first_name'],
                                    'last_name': row['last_name'],
                                    'is_active': True
                                }
                            )
                            
                            if created:
                                user.set_password('password123')  # Default password
                                user.save()
                                
                                # Create profile
                                UserProfile.objects.create(
                                    user=user,
                                    student_id=row.get('student_id', ''),
                                    department=department,
                                    course=course,
                                    year_level=row.get('year_level', ''),
                                    phone_number=row.get('phone_number', ''),
                                    is_verified=False
                                )
                                
                                imported_count += 1
                                self.stdout.write(f'  Imported: {user.username}')
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'  User {user.username} already exists, skipped')
                                )
                        
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(f'  Error importing row {row}: {str(e)}')
                            )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Import completed: {imported_count} users imported, {error_count} errors'
                    )
                )
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {filename}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file: {str(e)}')
            )

    def export_users(self, filename):
        """Export users to CSV file"""
        self.stdout.write(f'Exporting users to {filename}...')
        
        users = User.objects.select_related('userprofile', 'userprofile__department', 'userprofile__course').all()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'username', 'email', 'first_name', 'last_name', 'student_id',
                'department_name', 'department_code', 'course_name', 'course_code',
                'year_level', 'phone_number', 'is_verified', 'is_active', 'date_joined'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            exported_count = 0
            
            for user in users:
                profile = getattr(user, 'userprofile', None)
                
                row = {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'student_id': profile.student_id if profile else '',
                    'department_name': profile.department.name if profile and profile.department else '',
                    'department_code': profile.department.code if profile and profile.department else '',
                    'course_name': profile.course.name if profile and profile.course else '',
                    'course_code': profile.course.code if profile and profile.course else '',
                    'year_level': profile.year_level if profile else '',
                    'phone_number': profile.phone_number if profile else '',
                    'is_verified': profile.is_verified if profile else False,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                writer.writerow(row)
                exported_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Export completed: {exported_count} users exported to {filename}')
        )
