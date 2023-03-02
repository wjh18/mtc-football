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
    def with_extras(self):
        return self.annotate(
            is_american=conference_case("American"),
            is_national=conference_case("National"),
            is_divisional=is_conf_or_div_case("div"),
            is_conference=is_conf_or_div_case("conf"),
        ).order_by("-is_american", "-is_national", "-is_divisional", "-is_conference")

    def completed_for_season(self, season):
        return self.filter(season=season, is_final=True)

    def filter_by_team(self, team):
        return self.filter(Q(home_team=team) | Q(away_team=team))

    def mark_is_divisional(self):
        return self.annotate(is_divisional=is_conf_or_div_case("div"))

    def mark_is_conference(self):
        return self.annotate(is_conference=is_conf_or_div_case("conf"))

    def completed_for_season_by_team(self, season, team):
        return (
            self.completed_for_season(season)
            .filter_by_team(team)
            .mark_is_divisional()  # Divisional wins are also in-conference!
            .mark_is_conference()
        )

    def completed_for_season_by_team_in_div(self, season, team):
        return self.completed_for_season_by_team(season, team).filter(
            is_divisional=True
        )

    def completed_for_season_by_team_in_conf(self, season, team):
        return self.completed_for_season_by_team(season, team).filter(
            is_divisional=False, is_conference=True
        )  # Don't include divisional

    def completed_for_season_by_team_non_conf(self, season, team):
        return self.completed_for_season_by_team(season, team).filter(
            is_conference=False
        )

    def home_or_away_wins(self, team):
        home_or_away_wins = (Q(home_score__gt=F("away_score")) & Q(home_team=team)) | (
            Q(away_score__gt=F("home_score")) & Q(away_team=team)
        )
        return self.filter(home_or_away_wins)

    def home_or_away_losses(self, team):
        home_or_away_losses = (
            Q(home_score__lt=F("away_score")) & Q(home_team=team)
        ) | (Q(away_score__lt=F("home_score")) & Q(away_team=team))
        return self.filter(home_or_away_losses)

    def home_or_away_ties(self):
        home_or_away_ties = Q(home_score=F("away_score"))
        return self.filter(home_or_away_ties)

    def last_5(self, season, team):
        return self.completed_for_season_by_team(season, team).order_by("-week_number")[
            :5
        ]
