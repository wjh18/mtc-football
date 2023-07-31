from django.db import models
from django.db.models import Case, F, Q, When
from django.db.models.fields import BooleanField


def is_conf_name_case(conf_name: str):
    """
    Case for determining whether the teams in a matchup both belong
    to the passed conference (if it even IS a conference matchup).
    """
    return Case(
        When(
            home_team__conference__name=conf_name,
            away_team__conference__name=conf_name,
            then=True,
        ),
        default=False,
        output_field=BooleanField(),
    )


def is_conf_matchup_case():
    """
    Case for determining whether the matchup is a conference matchup
    (both teams belong to the same conference).
    """
    return Case(
        When(
            Q(home_team__conference=F("away_team__conference")),
            then=True,
        ),
        default=False,
        output_field=BooleanField(),
    )


def is_div_matchup_case():
    """
    Case for determining whether the matchup is a division matchup
    (both teams belong to the same division).
    """
    return Case(
        When(
            Q(home_team__division=F("away_team__division")),
            then=True,
        ),
        default=False,
        output_field=BooleanField(),
    )


class MatchupManager(models.Manager):
    def get_queryset(self):
        return MatchupQuerySet(self.model, using=self._db).select_related(
            "home_team__league",
            "home_team__conference",
            "home_team__division",
            "away_team__league",
            "away_team__conference",
            "away_team__division",
            "season__league",
        )


class MatchupQuerySet(models.QuerySet):
    def with_cases(self):
        return self.annotate(
            is_american=is_conf_name_case("American"),
            is_national=is_conf_name_case("National"),
            is_divisional=is_div_matchup_case(),
            is_conference=is_conf_matchup_case(),
        ).order_by("-is_american", "-is_national", "-is_divisional", "-is_conference")

    def filter_by_team(self, team):
        return self.filter(Q(home_team=team) | Q(away_team=team))

    def filter_by_reg_season(self, season):
        return self.filter(season=season, week_number__lte=18)
