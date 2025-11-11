from django.apps import AppConfig


class SecurityModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security_module'
    verbose_name = 'Security Management'
    
    def ready(self):
        import security_module.signals
