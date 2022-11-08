from django.db import models
from django.db.models import Case, When
from django.db.models.fields import BooleanField


def conference_case(conf_name):
    return Case(
        When(
            home_team__conference__name=conf_name,
            away_team__conference__name=conf_name,
            then=True,
        ),
        default=False,
        output_field=BooleanField(),
    )


class MatchupManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "home_team__league",
                "home_team__conference",
                "home_team__division",
                "away_team__league",
                "away_team__conference",
                "away_team__division",
                "scoreboard",
                "season__league",
            )
        )

    def with_extras(self):
        return self.annotate(
            is_american=conference_case("American"),
            is_national=conference_case("National"),
        ).order_by("-is_american", "-is_national", "-is_divisional", "-is_conference")
