from django.db import models


class TeamStandingManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("team__league", "team__conference", "team__division")
        )
