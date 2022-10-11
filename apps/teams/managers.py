from django.db import models


class TeamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("league", "conference", "division")
