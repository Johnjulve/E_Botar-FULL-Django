from django.apps import AppConfig


class VotingModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voting_module'
    verbose_name = 'Voting Management'
    
    def ready(self):
        import voting_module.signals
