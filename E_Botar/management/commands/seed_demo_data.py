from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from auth_module.models import UserProfile, Department, Course
from election_module.models import SchoolElection, ElectionPosition, SchoolPosition, Party
from candidate_module.models import Candidate, CandidateApplication
from voting_module.models import SchoolVote, VoteReceipt, AnonVote, EncryptedBallot
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with comprehensive sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before populating')
        parser.add_argument('--users', type=int, default=50, help='Number of sample users to create')
        parser.add_argument('--elections', type=int, default=2, help='Number of sample elections to create')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        self.create_departments_and_courses()
        self.create_sample_users(options['users'])
        self.create_sample_elections(options['elections'])
        self.create_sample_candidates()
        self.create_sample_votes()
        
        self.stdout.write(
            self.style.SUCCESS('Sample data populated successfully!')
        )

    def clear_data(self):
        """Clear existing sample data"""
        self.stdout.write('Clearing existing data...')
        
        # Clear votes and related data
        SchoolVote.objects.all().delete()
        VoteReceipt.objects.all().delete()
        AnonVote.objects.all().delete()
        EncryptedBallot.objects.all().delete()
        
        # Clear candidates
        Candidate.objects.all().delete()
        CandidateApplication.objects.all().delete()
        
        # Clear elections
        SchoolElection.objects.all().delete()
        ElectionPosition.objects.all().delete()
        SchoolPosition.objects.all().delete()
        Party.objects.all().delete()
        
        # Clear users (except superusers)
        User.objects.filter(is_superuser=False).delete()
        UserProfile.objects.all().delete()
        
        self.stdout.write('Data cleared successfully!')

    def create_departments_and_courses(self):
        """Create sample departments and courses"""
        self.stdout.write('Creating departments and courses...')
        
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS', 'courses': [
                {'name': 'Bachelor of Science in Computer Science', 'code': 'BSCS'},
                {'name': 'Bachelor of Science in Information Technology', 'code': 'BSIT'},
                {'name': 'Bachelor of Science in Computer Engineering', 'code': 'BSCE'},
            ]},
            {'name': 'Engineering', 'code': 'ENG', 'courses': [
                {'name': 'Bachelor of Science in Civil Engineering', 'code': 'BSCE'},
                {'name': 'Bachelor of Science in Electrical Engineering', 'code': 'BSEE'},
                {'name': 'Bachelor of Science in Mechanical Engineering', 'code': 'BSME'},
            ]},
            {'name': 'Business Administration', 'code': 'BA', 'courses': [
                {'name': 'Bachelor of Science in Business Administration', 'code': 'BSBA'},
                {'name': 'Bachelor of Science in Accountancy', 'code': 'BSA'},
                {'name': 'Bachelor of Science in Marketing', 'code': 'BSM'},
            ]},
            {'name': 'Education', 'code': 'EDU', 'courses': [
                {'name': 'Bachelor of Elementary Education', 'code': 'BEED'},
                {'name': 'Bachelor of Secondary Education', 'code': 'BSED'},
                {'name': 'Bachelor of Science in Psychology', 'code': 'BSP'},
            ]},
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'code': dept_data['code']}
            )
            
            if created:
                self.stdout.write(f'Created department: {department.name}')
            
            for course_data in dept_data['courses']:
                course, created = Course.objects.get_or_create(
                    department=department,
                    name=course_data['name'],
                    defaults={'code': course_data['code']}
                )
                
                if created:
                    self.stdout.write(f'  - Created course: {course.name}')

    def create_sample_users(self, count):
        """Create sample users with profiles"""
        self.stdout.write(f'Creating {count} sample users...')
        
        departments = list(Department.objects.all())
        courses = list(Course.objects.all())
        
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica', 'Robert', 'Ashley']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            student_id = f"2024-{10000 + i}"
            
            # Create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Create profile
                UserProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    department=random.choice(departments) if departments else None,
                    course=random.choice(courses) if courses else None,
                    year_level=random.choice(['1st Year', '2nd Year', '3rd Year', '4th Year']),
                    phone_number=f"09{random.randint(100000000, 999999999)}",
                    is_verified=random.choice([True, False])
                )
                
                if i % 10 == 0:
                    self.stdout.write(f'Created {i+1} users...')

    def create_sample_elections(self, count):
        """Create sample elections with positions"""
        self.stdout.write(f'Creating {count} sample elections...')
        
        positions_data = [
            {'name': 'Student Council President', 'description': 'Head of student government'},
            {'name': 'Student Council Vice President', 'description': 'Vice head of student government'},
            {'name': 'Student Council Secretary', 'description': 'Handles documentation and records'},
            {'name': 'Student Council Treasurer', 'description': 'Manages student funds'},
            {'name': 'Student Council Auditor', 'description': 'Oversees financial transparency'},
        ]
        
        # Create positions
        for pos_data in positions_data:
            position, created = SchoolPosition.objects.get_or_create(
                name=pos_data['name'],
                defaults={'description': pos_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created position: {position.name}')
        
        # Create elections
        for i in range(count):
            election_title = f"School Year 2024-2025 Election {i+1}"
            start_date = timezone.now() + timedelta(days=i*30)
            end_date = start_date + timedelta(days=7)
            
            election, created = SchoolElection.objects.get_or_create(
                title=election_title,
                defaults={
                    'description': f'Student government election for {election_title}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': i == 0  # Only first election is active
                }
            )
            
            if created:
                self.stdout.write(f'Created election: {election.title}')
                
                # Create election positions
                for position in SchoolPosition.objects.all():
                    ElectionPosition.objects.create(
                        election=election,
                        position=position,
                        order=position.id
                    )

    def create_sample_candidates(self):
        """Create sample candidates and applications"""
        self.stdout.write('Creating sample candidates...')
        
        # Create parties
        parties_data = [
            {'name': 'Progressive Students Alliance', 'description': 'Focused on student welfare and campus improvements'},
            {'name': 'Academic Excellence Party', 'description': 'Committed to academic excellence and research'},
            {'name': 'Unity and Diversity Coalition', 'description': 'Promoting inclusivity and campus unity'},
        ]
        
        for party_data in parties_data:
            party, created = Party.objects.get_or_create(
                name=party_data['name'],
                defaults={'description': party_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created party: {party.name}')
        
        # Create candidate applications
        users = User.objects.filter(is_superuser=False)[:20]  # First 20 users
        elections = SchoolElection.objects.all()
        parties = list(Party.objects.all())
        
        for election in elections:
            for position in election.positions.all():
                # Select 2-3 random users as candidates for each position
                candidates_count = random.randint(2, 3)
                selected_users = random.sample(list(users), min(candidates_count, len(users)))
                
                for user in selected_users:
                    application, created = CandidateApplication.objects.get_or_create(
                        user=user,
                        election=election,
                        position=position.position,
                        defaults={
                            'party': random.choice(parties),
                            'manifesto': f"I am committed to serving as {position.position.name} and will work tirelessly to represent student interests.",
                            'status': random.choice(['pending', 'approved', 'rejected']),
                            'photo': None
                        }
                    )
                    
                    if created and application.status == 'approved':
                        # Create candidate if approved
                        Candidate.objects.create(
                            user=user,
                            election=election,
                            position=position.position,
                            party=application.party,
                            manifesto=application.manifesto,
                            photo=application.photo
                        )

    def create_sample_votes(self):
        """Create sample votes for active elections"""
        self.stdout.write('Creating sample votes...')
        
        active_elections = SchoolElection.objects.filter(is_active=True)
        
        for election in active_elections:
            voters = User.objects.filter(is_superuser=False)[:30]  # First 30 users vote
            
            for voter in voters:
                for position in election.positions.all():
                    candidates = Candidate.objects.filter(
                        election=election,
                        position=position.position
                    )
                    
                    if candidates.exists():
                        # Randomly select a candidate to vote for
                        selected_candidate = random.choice(candidates)
                        
                        # Create vote (if not already exists)
                        vote, created = SchoolVote.objects.get_or_create(
                            voter=voter,
                            election=election,
                            position=position.position,
                            defaults={'candidate': selected_candidate}
                        )
                        
                        if created:
                            # Create anonymized vote for results
                            AnonVote.objects.create(
                                election=election,
                                position=position.position,
                                candidate=selected_candidate
                            )
