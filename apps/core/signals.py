from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SiteSettings


@receiver(post_save, sender=Site)
def create_site_settings(sender, instance, **kwargs):
    """
    Creates/updates a SiteSettings object after a Site object.
    """
    site_settings, created = SiteSettings.objects.update_or_create(site=instance)

    if not created:
        site_settings.save()
