from django.apps import AppConfig

class C2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'C2'

    def ready(self):
        import C2.signals  # Ensure signals are loaded
