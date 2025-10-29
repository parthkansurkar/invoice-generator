# invoice_app/apps.py
from django.apps import AppConfig

class InvoiceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice_app'
    
    def ready(self):
        import invoice_app.signals