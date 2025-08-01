# boutique/apps.py
from django.apps import AppConfig

class SalonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'salon'

    def ready(self):
        # Importer les signaux ici pour qu'ils soient reconnus par Django
        import salon.signals