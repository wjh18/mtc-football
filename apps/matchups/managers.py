from django.db import models
from django.db.models import Case, F, Q, When
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


def is_conf_or_div_case(conf_or_div):
    if conf_or_div == "conf":
        query = Q(home_team__conference=F("away_team__conference"))
    elif conf_or_div == "div":
        query = Q(home_team__division=F("away_team__division"))

    case = Case(
        When(
            query,
            then=True,
        ),
        default=False,
        output_field=BooleanField(),
    )
    return case


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
            is_divisional=is_conf_or_div_case("div"),
            is_conference=is_conf_or_div_case("conf"),
        ).order_by("-is_american", "-is_national", "-is_divisional", "-is_conference")
