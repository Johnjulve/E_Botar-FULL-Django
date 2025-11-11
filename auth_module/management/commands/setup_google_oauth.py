from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth for django-allauth'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')
        parser.add_argument('--domain', type=str, default='localhost:8000', help='Domain for the site')

    def handle(self, *args, **options):
        # Update or create the site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': options['domain'],
                'name': 'E-Botar Election System'
            }
        )
        
        if not created:
            site.domain = options['domain']
            site.name = 'E-Botar Election System'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Updated site: {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))

        # Create or update Google OAuth app
        if options['client_id'] and options['client_secret']:
            app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth',
                    'client_id': options['client_id'],
                    'secret': options['client_secret'],
                }
            )
            
            if not created:
                app.client_id = options['client_id']
                app.secret = options['client_secret']
                app.save()
                self.stdout.write(self.style.SUCCESS('Updated Google OAuth app'))
            else:
                self.stdout.write(self.style.SUCCESS('Created Google OAuth app'))
            
            # Add the site to the app
            app.sites.add(site)
            
            self.stdout.write(self.style.SUCCESS('Google OAuth setup complete!'))
            self.stdout.write(self.style.WARNING('Make sure to configure your Google OAuth credentials in Google Cloud Console'))
        else:
            self.stdout.write(self.style.WARNING('Please provide --client-id and --client-secret'))
            self.stdout.write(self.style.WARNING('Example: python manage.py setup_google_oauth --client-id "your-client-id" --client-secret "your-client-secret"'))
