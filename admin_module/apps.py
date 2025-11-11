from django.apps import AppConfig


class AdminModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_module'
    verbose_name = 'Administration Management'
    
    def ready(self):
        import admin_module.signals
