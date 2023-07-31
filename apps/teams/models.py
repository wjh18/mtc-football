from django.db import models
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property

from apps.matchups.models import Matchup

from .managers import TeamManager


class Team(models.Model):
    league = models.ForeignKey(
        "leagues.League",
        on_delete=models.CASCADE,
        related_name="teams",
    )
    conference = models.ForeignKey(
        "leagues.Conference",
        on_delete=models.CASCADE,
        related_name="teams",
    )
    division = models.ForeignKey(
        "leagues.Division",
        on_delete=models.CASCADE,
        related_name="teams",
    )
    location = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=3)
    overall_rating = models.PositiveSmallIntegerField(default=1)
    slug = models.SlugField(blank=True, null=True)

    objects = TeamManager()

    class Meta:
        ordering = ["location"]

    def __str__(self):
        return f"{self.location} {self.name} ({self.abbreviation})"

    def update_team_overall(self) -> None:
        """
        Called when player ratings are changed to update team rating.
        """
        team_overall = self.player_set.aggregate(Avg("overall_rating"))
        self.overall_rating = team_overall["overall_rating__avg"]
        self.save()

    @property
    def bye_week(self) -> int | None:
        """Find a team's bye week based on their season matchups."""
        season = self.league.current_season
        bye_week = None

        team_matchups = Matchup.objects.filter_by_team(self).filter_by_reg_season(
            season
        )
        possible_weeks = set(range(1, 19))
        matchup_weeks = team_matchups.values_list("week_number", flat=True)
        for m_week in matchup_weeks:
            possible_weeks.remove(m_week)

        if possible_weeks:
            bye_week = possible_weeks.pop()

        return bye_week

    @property
    def current_record(self) -> str:
        """Get a team's current W/L/T record"""
        season = self.league.current_season
        standing = get_object_or_404(self.team_standings.all(), season=season)
        return f"({standing.wins}-{standing.losses}-{standing.ties})"

    def get_absolute_url(self):
        return reverse("teams:team_detail", args=[self.league.slug, self.slug])


class UserTeam(models.Model):
    league = models.ForeignKey(
        "leagues.League",
        on_delete=models.CASCADE,
        related_name="user_teams",
    )
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    is_active_team = models.BooleanField(default=True)

    @cached_property
    def user(self):
        return self.league.user

    def __str__(self):
        return f"User team - {self.team.abbreviation} - {self.league}"
