from django.apps import AppConfig


class ElectionModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'election_module'
    verbose_name = 'Election Management'
    
    def ready(self):
        import election_module.signals
