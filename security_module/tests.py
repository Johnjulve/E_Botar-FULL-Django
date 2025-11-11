from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import SecurityEvent, SecurityLog, AccessAttempt, SecuritySettings, BlockedIP, SecurityAlert


class SecurityEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
    
    def test_security_event_creation(self):
        event = SecurityEvent.objects.create(
            user=self.user,
            event_type='login_attempt',
            severity='medium',
            description='User attempted to login',
            ip_address='127.0.0.1'
        )
        # Check that the string representation contains the expected parts
        str_repr = str(event)
        self.assertIn('login_attempt', str_repr)
        self.assertIn('medium', str_repr)
        self.assertEqual(event.event_type, 'login_attempt')
        self.assertEqual(event.severity, 'medium')
    
    def test_security_event_without_user(self):
        event = SecurityEvent.objects.create(
            user=None,
            event_type='suspicious_activity',
            severity='high',
            description='Suspicious activity detected',
            ip_address='192.168.1.1'
        )
        self.assertIsNone(event.user)
        self.assertEqual(event.event_type, 'suspicious_activity')


class SecurityLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
    
    def test_security_log_creation(self):
        log = SecurityLog.objects.create(
            user=self.user,
            level='info',
            message='User logged in successfully',
            ip_address='127.0.0.1'
        )
        # Check that the string representation contains the expected parts
        str_repr = str(log)
        self.assertIn('info', str_repr)
        self.assertIn('User logged in successfully', str_repr)
        self.assertEqual(log.level, 'info')
        self.assertEqual(log.message, 'User logged in successfully')


class AccessAttemptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
    
    def test_successful_access_attempt(self):
        attempt = AccessAttempt.objects.create(
            user=self.user,
            username='testuser',
            success=True,
            ip_address='127.0.0.1'
        )
        # Check that the string representation contains the expected parts
        str_repr = str(attempt)
        self.assertIn('testuser', str_repr)
        self.assertIn('Success', str_repr)
        self.assertTrue(attempt.success)
        self.assertEqual(attempt.username, 'testuser')
    
    def test_failed_access_attempt(self):
        attempt = AccessAttempt.objects.create(
            user=None,
            username='invaliduser',
            success=False,
            ip_address='127.0.0.1'
        )
        # Check that the string representation contains the expected parts
        str_repr = str(attempt)
        self.assertIn('invaliduser', str_repr)
        self.assertIn('Failed', str_repr)
        self.assertFalse(attempt.success)
        self.assertIsNone(attempt.user)


class SecuritySettingsModelTest(TestCase):
    def test_security_settings_creation(self):
        setting = SecuritySettings.objects.create(
            name='max_login_attempts',
            value='5',
            description='Maximum login attempts before lockout'
        )
        self.assertEqual(str(setting), "max_login_attempts: 5")
        self.assertEqual(setting.name, 'max_login_attempts')
        self.assertEqual(setting.value, '5')


class BlockedIPModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com"
        )
    
    def test_blocked_ip_creation(self):
        blocked_ip = BlockedIP.objects.create(
            ip_address='192.168.1.100',
            reason='Suspicious activity',
            blocked_by=self.user
        )
        self.assertEqual(str(blocked_ip), "192.168.1.100 - Suspicious activity")
        self.assertEqual(blocked_ip.ip_address, '192.168.1.100')
        self.assertTrue(blocked_ip.is_active)


class SecurityAlertModelTest(TestCase):
    def test_security_alert_creation(self):
        alert = SecurityAlert.objects.create(
            alert_type='threat_detected',
            title='Suspicious Login Pattern',
            description='Multiple failed login attempts detected',
            severity='high'
        )
        self.assertEqual(str(alert), "threat_detected - Suspicious Login Pattern")
        self.assertEqual(alert.alert_type, 'threat_detected')
        self.assertFalse(alert.is_resolved)
