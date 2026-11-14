from django.apps import AppConfig
import os

class DigitalmarketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'digitalmarketing'

    def ready(self):

        # Prevent scheduler during migrations
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .scheduler import start
        start()
