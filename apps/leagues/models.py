from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.utils import random_string_generator as random_string

from .setup import create_league_structure


class League(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="leagues"
    )
    name = models.CharField(max_length=50)
    gm_name = models.CharField(max_length=50)
    creation_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # Generate a unique slug
        if not self.slug:
            self.slug = slugify(self.name + "-" + random_string())
        # False if saving an existing instance
        no_instance_exists = self._state.adding
        # Save League instance before creating its structure
        super().save(*args, **kwargs)
        # Only create structure on initial save() call
        if no_instance_exists:
            create_league_structure(self)

    def get_absolute_url(self):
        return reverse("leagues:league_detail", args=[self.slug])


class Conference(models.Model):
    name = models.CharField(max_length=50)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="conferences"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.league}"


class Division(models.Model):
    name = models.CharField(max_length=200)
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="divisions"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.conference.league}"
