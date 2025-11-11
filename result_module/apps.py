from django.apps import AppConfig


class ResultModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'result_module'
    verbose_name = 'Results Management'
    
    def ready(self):
        import result_module.signals
