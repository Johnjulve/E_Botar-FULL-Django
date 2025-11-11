from django.test import TestCase
from django.contrib.auth.models import User
from auth_module.models import Department, Course, UserProfile, ActivityLog


class DepartmentModelTest(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
            description="Computer Science Department"
        )
        self.assertEqual(str(department), "Computer Science (CS)")
        self.assertTrue(department.is_active)


class CourseModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            code="ENG"
        )
    
    def test_course_creation(self):
        course = Course.objects.create(
            department=self.department,
            name="Software Engineering",
            code="SE101"
        )
        self.assertEqual(str(course), "Software Engineering (SE101) - Engineering")
        self.assertTrue(course.is_active)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        self.department = Department.objects.create(
            name="Computer Science",
            code="CS"
        )
    
    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(
            user=self.user,
            student_id="2024001",
            department=self.department,
            year_level="3rd Year"
        )
        self.assertEqual(str(profile), "Test User (2024001)")
        self.assertFalse(profile.is_verified)


class ActivityLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
    
    def test_activity_log_creation(self):
        log = ActivityLog.objects.create(
            user=self.user,
            action_type="login",
            description="User logged in successfully",
            ip_address="127.0.0.1"
        )
        self.assertIn("testuser", str(log))
        self.assertEqual(log.action_type, "login")