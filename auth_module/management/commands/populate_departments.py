from django.core.management.base import BaseCommand
from auth_module.models import Department, Course


class Command(BaseCommand):
    help = 'Populate database with default departments and courses'

    def handle(self, *args, **options):
        # Create departments
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS', 'description': 'Computer Science Department'},
            {'name': 'Engineering', 'code': 'ENG', 'description': 'Engineering Department'},
            {'name': 'Business Administration', 'code': 'BA', 'description': 'Business Administration Department'},
            {'name': 'Education', 'code': 'EDU', 'description': 'Education Department'},
            {'name': 'Arts and Sciences', 'code': 'AS', 'description': 'Arts and Sciences Department'},
            {'name': 'Nursing', 'code': 'NUR', 'description': 'Nursing Department'},
        ]

        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')

        # Create courses for each department
        courses_data = {
            'CS': [
                {'name': 'Bachelor of Science in Computer Science', 'code': 'BSCS'},
                {'name': 'Bachelor of Science in Information Technology', 'code': 'BSIT'},
                {'name': 'Bachelor of Science in Information Systems', 'code': 'BSIS'},
            ],
            'ENG': [
                {'name': 'Bachelor of Science in Civil Engineering', 'code': 'BSCE'},
                {'name': 'Bachelor of Science in Electrical Engineering', 'code': 'BSEE'},
                {'name': 'Bachelor of Science in Mechanical Engineering', 'code': 'BSME'},
            ],
            'BA': [
                {'name': 'Bachelor of Science in Business Administration', 'code': 'BSBA'},
                {'name': 'Bachelor of Science in Accountancy', 'code': 'BSA'},
                {'name': 'Bachelor of Science in Marketing', 'code': 'BSM'},
            ],
            'EDU': [
                {'name': 'Bachelor of Elementary Education', 'code': 'BEED'},
                {'name': 'Bachelor of Secondary Education', 'code': 'BSED'},
                {'name': 'Bachelor of Science in Education', 'code': 'BSE'},
            ],
            'AS': [
                {'name': 'Bachelor of Arts in English', 'code': 'BAENG'},
                {'name': 'Bachelor of Science in Psychology', 'code': 'BSP'},
                {'name': 'Bachelor of Science in Biology', 'code': 'BSBIO'},
            ],
            'NUR': [
                {'name': 'Bachelor of Science in Nursing', 'code': 'BSN'},
                {'name': 'Bachelor of Science in Midwifery', 'code': 'BSM'},
            ],
        }

        for dept_code, courses in courses_data.items():
            try:
                department = Department.objects.get(code=dept_code)
                for course_data in courses:
                    course, created = Course.objects.get_or_create(
                        department=department,
                        code=course_data['code'],
                        defaults=course_data
                    )
                    if created:
                        self.stdout.write(f'Created course: {course.name}')
            except Department.DoesNotExist:
                self.stdout.write(f'Department {dept_code} not found')

        self.stdout.write(self.style.SUCCESS('Successfully populated departments and courses'))
