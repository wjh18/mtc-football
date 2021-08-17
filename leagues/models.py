import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .utils import (
    read_player_names_from_csv,
    read_team_info_from_csv
)


class League(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=300)
    creation_date = models.DateTimeField(default=timezone.now)
    commissioner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    commissioner_name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("league_detail", args=[str(self.id)])
    