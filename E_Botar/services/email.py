from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Consolidated email service for all email operations"""
    
    @staticmethod
    def send_welcome_email(user: User, password: str = None):
        """Send welcome email to new user"""
        try:
            subject = 'Welcome to E-Botar Voting System'
            context = {
                'user': user,
                'password': password,
                'login_url': f"{settings.SITE_URL}/login/" if hasattr(settings, 'SITE_URL') else '/login/'
            }
            
            html_content = render_to_string('emails/welcome.html', context)
            text_content = render_to_string('emails/welcome.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Welcome email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user: User, reset_token: str):
        """Send password reset email"""
        try:
            subject = 'Password Reset - E-Botar Voting System'
            reset_url = f"{settings.SITE_URL}/reset-password/{reset_token}/" if hasattr(settings, 'SITE_URL') else f"/reset-password/{reset_token}/"
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_in': '24 hours'
            }
            
            html_content = render_to_string('emails/password_reset.html', context)
            text_content = render_to_string('emails/password_reset.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Password reset email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_election_notification(election, users: list, notification_type: str):
        """Send election notifications to users"""
        try:
            if notification_type == 'start':
                subject = f'Election Started: {election.title}'
                template = 'emails/election_started.html'
            elif notification_type == 'end':
                subject = f'Election Ended: {election.title}'
                template = 'emails/election_ended.html'
            elif notification_type == 'reminder':
                subject = f'Election Reminder: {election.title}'
                template = 'emails/election_reminder.html'
            else:
                return False
            
            context = {
                'election': election,
                'voting_url': f"{settings.SITE_URL}/vote/{election.id}/" if hasattr(settings, 'SITE_URL') else f"/vote/{election.id}/"
            }
            
            html_content = render_to_string(template, context)
            text_content = render_to_string(template.replace('.html', '.txt'), context)
            
            # Send to multiple users
            for user in users:
                if user.email:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
            
            logger.info(f"Election notification sent to {len(users)} users")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send election notification: {str(e)}")
            return False
    
    @staticmethod
    def send_candidate_application_notification(application, admin_users: list):
        """Send notification to admins about new candidate application"""
        try:
            subject = f'New Candidate Application: {application.user.get_full_name()}'
            
            context = {
                'application': application,
                'review_url': f"{settings.SITE_URL}/admin/candidates/application/{application.id}/" if hasattr(settings, 'SITE_URL') else f"/admin/candidates/application/{application.id}/"
            }
            
            html_content = render_to_string('emails/candidate_application.html', context)
            text_content = render_to_string('emails/candidate_application.txt', context)
            
            for admin in admin_users:
                if admin.email:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[admin.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
            
            logger.info(f"Candidate application notification sent to {len(admin_users)} admins")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send candidate application notification: {str(e)}")
            return False
    
    @staticmethod
    def send_vote_receipt(user: User, election, receipt_code: str):
        """Send vote receipt to user"""
        try:
            subject = f'Vote Receipt - {election.title}'
            
            context = {
                'user': user,
                'election': election,
                'receipt_code': receipt_code,
                'timestamp': timezone.now()
            }
            
            html_content = render_to_string('emails/vote_receipt.html', context)
            text_content = render_to_string('emails/vote_receipt.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Vote receipt sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send vote receipt to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_system_notification(users: list, subject: str, message: str, notification_type: str = 'info'):
        """Send system-wide notifications"""
        try:
            context = {
                'message': message,
                'notification_type': notification_type,
                'timestamp': timezone.now()
            }
            
            html_content = render_to_string('emails/system_notification.html', context)
            text_content = render_to_string('emails/system_notification.txt', context)
            
            for user in users:
                if user.email:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
            
            logger.info(f"System notification sent to {len(users)} users")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send system notification: {str(e)}")
            return False


def send_bulk_emails(recipients: list, subject: str, message: str, template: str = None):
    """Send bulk emails to multiple recipients"""
    try:
        if template:
            html_content = render_to_string(template, {'message': message})
            text_content = message
        else:
            html_content = None
            text_content = message
        
        for recipient in recipients:
            if recipient.email:
                if html_content:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[recipient.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                else:
                    send_mail(
                        subject=subject,
                        message=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False
                    )
        
        logger.info(f"Bulk emails sent to {len(recipients)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send bulk emails: {str(e)}")
        return False
