from django.contrib.sites.models import Site
from django.db import models


class BaseModel(models.Model):
    """
    Base model that includes default created / updated timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    meta_description = models.CharField(
        max_length=255,
        help_text="Default description used in SEO metadata",
        default="Move the Chains is a web-based (American) football simulation game",
    )
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Twitter handle with @ used in SEO metadata",
    )
    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Default author used in SEO metadata",
    )
    default_image = models.ImageField(
        upload_to="core/",
        blank=True,
        null=True,
        help_text="Default site image used in SEO metadata",
    )
    og_type = models.CharField(
        max_length=255,
        default="website",
        help_text="Default og:type for Open Graph protocol",
    )
    tc_type = models.CharField(
        max_length=255,
        default="summary",
        help_text="Default twitter:card type for Twitter Cards",
    )
    server_root = models.URLField(
        default="http://localhost:8000",
        help_text="Default server root used in SEO metadata",
    )

    def __str__(self):
        return self.site.name

    class Meta:
        verbose_name_plural = "settings"
