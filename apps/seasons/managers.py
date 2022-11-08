from django.db import models
from django.db.models import Case, F, FloatField, When
from django.db.models.functions import Cast


class TeamStandingManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("team__league", "team__conference", "team__division")
        )

    def with_extras(self):
        return self.annotate(
            pt_diff=F("points_for") - F("points_against"),
            win_pct=Case(
                When(
                    wins__gt=0,
                    then=Cast("wins", FloatField())
                    / (F("wins") + F("losses") + F("ties")),
                ),
                default=F("wins"),
                output_field=FloatField(),
            ),
        )
