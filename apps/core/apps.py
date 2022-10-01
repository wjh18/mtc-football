from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate, post_save


def create_default_site_settings(sender, **kwargs):
    """Creates default site settings after migration"""
    # App config must be ready for import to work
    from django.contrib.sites.models import Site

    from .models import SiteSettings

    site = Site.objects.get(id=getattr(settings, "SITE_ID", 1))

    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(site=site)


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # App config must be ready for import to work
        from django.contrib.sites.models import Site

        post_migrate.connect(create_default_site_settings, sender=self)
        from .signals import create_site_settings

        post_save.connect(create_site_settings, sender=Site)
