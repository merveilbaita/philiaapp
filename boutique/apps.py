# boutique/apps.py
from django.apps import AppConfig

class BoutiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boutique'

    def ready(self):
        # Importer les signaux ici pour qu'ils soient reconnus par Django
        import boutique.signals