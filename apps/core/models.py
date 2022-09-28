from django.contrib.sites.models import Site
from django.db import models


class SiteSettings(models.Model):
    """
    Extension of the Sites model that holds more info about the site.
    """

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="settings",
        verbose_name="site",
    )
    meta_description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.site.name

    class Meta:
        app_label = "sites"
        verbose_name_plural = "settings"
