from datetime import date

from django.db import models
from django.http import Http404
from django.utils.functional import cached_property

from apps.seasons.managers import TeamStandingManager, TeamStandingQuerySet

from .services.setup import create_season_details


class Season(models.Model):
    PHASES = (
        (1, "Re-signing"),
        (2, "Free Agent Signing"),
        (3, "Draft"),
        (4, "Regular Season"),
        (5, "Playoffs"),
        (6, "Offseason"),
    )
    league = models.ForeignKey(
        "leagues.League",
        on_delete=models.CASCADE,
        related_name="seasons",
    )
    start_date = models.DateField(default=date(date.today().year, 8, 29))
    current_date = models.DateField(default=date(date.today().year, 8, 29))
    phase = models.PositiveSmallIntegerField(default=4, choices=PHASES)
    season_number = models.PositiveSmallIntegerField(default=1)
    week_number = models.PositiveSmallIntegerField(default=1)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"Season {self.season_number} - {self.league}"

    def save(self, *args, **kwargs):
        # False if saving an existing instance
        no_instance_exists = self._state.adding
        # Save Season instance before creating schedule
        super().save(*args, **kwargs)
        # Only create schedule on initial save() call
        if no_instance_exists:
            create_season_details(self)

    def get_byes(self, week_num=False):
        """Obtain teams with a bye week on the current week"""
        week_number = self.week_number if not week_num else week_num
        matchups = self.matchups.filter(week_number=week_number)

        home_team_ids = matchups.values_list("home_team", flat=True)
        away_team_ids = matchups.values_list("away_team", flat=True)
        team_ids = home_team_ids.union(away_team_ids)

        teams_with_bye = self.league.teams.exclude(id__in=team_ids)
        return teams_with_bye

    def week_number_from_kwargs(self, week_kw: int) -> int:
        """Return week number based on kwargs passed from view"""
        if self.week_number >= 23 and week_kw is None:
            # Playoffs over, default to showing championship round
            week_number = self.week_number - 1
        elif week_kw and (week_kw not in range(1, 23) or week_kw == 0):
            raise Http404("Invalid week number supplied")
        elif week_kw is None:
            week_number = self.week_number  # Default to current week
        else:
            week_number = week_kw  # Default to chosen week

        return week_number


class TeamStanding(models.Model):
    PLAYOFF_CLINCHES = (
        ("BYE", "Bye Week"),
        ("DIV", "Division"),
        ("BTH", "Playoff Berth"),
        ("OUT", "Out of Contention"),
    )
    PLAYOFF_ROUND_WINS = (
        ("WLD", "Wildcard"),
        ("DIV", "Divisional"),
        ("CNF", "Conference"),
        ("SHP", "Championship"),
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="team_standings",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="team_standings",
    )
    wins = models.SmallIntegerField(default=0)
    losses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    points_for = models.SmallIntegerField(default=0)
    points_against = models.SmallIntegerField(default=0)
    streak = models.SmallIntegerField(default=0)
    division_ranking = models.PositiveSmallIntegerField(default=1)
    conference_ranking = models.PositiveSmallIntegerField(default=1)
    power_ranking = models.PositiveSmallIntegerField(default=1)
    clinched = models.CharField(
        max_length=3, choices=PLAYOFF_CLINCHES, blank=True, null=True
    )
    round_won = models.CharField(
        max_length=3, choices=PLAYOFF_ROUND_WINS, blank=True, null=True
    )
    objects = TeamStandingManager.from_queryset(TeamStandingQuerySet)()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "season"], name="unique_team_standings_for_season"
            ),
        ]

    def __str__(self):
        return f"{self.team.abbreviation} standings - {self.season}"

    @cached_property
    def league(self):
        return self.season.league

    @cached_property
    def team_division(self):
        return self.team.division

    @cached_property
    def team_conference(self):
        return self.team.conference
