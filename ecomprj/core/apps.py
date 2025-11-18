from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Update Site domain for development"""
        from django.conf import settings
        from django.contrib.sites.models import Site
        
        if settings.DEBUG:
            try:
                site = Site.objects.get(pk=settings.SITE_ID)
                if site.domain == 'example.com':
                    site.domain = '127.0.0.1:8000'
                    site.name = 'Local Development'
                    site.save()
            except Exception:
                pass  # Site might not exist yet