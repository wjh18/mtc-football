from django.apps import apps
from django.db import models
from django.db.models import Avg
from django.urls import reverse

from apps.personnel.setup import create_team_players


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

    class Meta:
        ordering = ["location"]

    def __str__(self):
        return f"{self.location} {self.name} ({self.abbreviation})"

    def save(self, *args, **kwargs):
        # Generate a unique slug
        if not self.slug:
            self.slug = self.abbreviation
        # False if saving an existing instance
        no_instance_exists = self._state.adding
        # Save Team instance before creating players
        super().save(*args, **kwargs)
        # Only create players on initial save() call
        if no_instance_exists:
            create_team_players(self)

    def update_team_overall(self):
        """
        Called when player ratings are changed to update team rating.
        """
        team_overall = self.player_set.aggregate(Avg("overall_rating"))
        self.overall_rating = team_overall["overall_rating__avg"]
        self.save()

    def check_bye_week(self, season):
        """Find a team's bye week"""
        home_matchup_weeks = self.home_matchups.filter(
            season=season, is_postseason=False
        ).values_list("week_number", flat=True)
        away_matchup_weeks = self.away_matchups.filter(
            season=season, is_postseason=False
        ).values_list("week_number", flat=True)

        matchup_weeks = home_matchup_weeks.union(away_matchup_weeks)
        weeks_set = {w for w in range(1, 19)}
        bye_week = list(weeks_set - set(matchup_weeks))[0]

        return bye_week

    def get_current_record(self):
        """Get a team's current W/L/T record"""
        Season = apps.get_model("seasons.Season")
        TeamStanding = apps.get_model("seasons.TeamStanding")

        season = Season.objects.get(league=self.league, is_current=True)

        standing = TeamStanding.objects.get(team=self, season=season)
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

    def __str__(self):
        return f"User team - {self.team.abbreviation} - {self.league}"
