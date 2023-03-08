from datetime import date

from django.db import models
from django.db.models import F, Q
from django.utils.functional import cached_property

from apps.matchups.models import Matchup
from apps.seasons.managers import TeamStandingManager

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
    objects = TeamStandingManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "season"], name="unique_team_standings_for_season"
            ),
        ]

    def __str__(self):
        return f"{self.team.abbreviation} standings - {self.season}"

    @cached_property
    def get_league(self):
        return self.season.league

    @property
    def home_wins(self):
        query = Q(home_score__gt=F("away_score")) & Q(home_team=self.team)
        home_win_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return home_win_count

    @property
    def away_wins(self):
        query = Q(away_score__gt=F("home_score")) & Q(away_team=self.team)
        away_win_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return away_win_count

    @property
    def home_losses(self):
        query = Q(home_score__lt=F("away_score")) & Q(home_team=self.team)
        home_loss_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return home_loss_count

    @property
    def away_losses(self):
        query = Q(away_score__lt=F("home_score")) & Q(away_team=self.team)
        away_loss_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return away_loss_count

    @property
    def home_ties(self):
        query = Q(home_score=F("away_score")) & Q(home_team=self.team)
        home_tie_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return home_tie_count

    @property
    def away_ties(self):
        query = Q(away_score=F("home_score")) & Q(away_team=self.team)
        away_tie_count = (
            Matchup.objects.completed_for_season_by_team(self.season, self.team)
            .filter(query)
            .count()
        )
        return away_tie_count

    @property
    def div_wins(self):
        div_win_count = (
            Matchup.objects.completed_for_season_by_team_in_div(self.season, self.team)
            .home_or_away_wins(self.team)
            .count()
        )
        return div_win_count

    @property
    def div_losses(self):
        div_loss_count = (
            Matchup.objects.completed_for_season_by_team_in_div(self.season, self.team)
            .home_or_away_losses(self.team)
            .count()
        )
        return div_loss_count

    @property
    def div_ties(self):
        div_tie_count = (
            Matchup.objects.completed_for_season_by_team_in_div(self.season, self.team)
            .home_or_away_ties()
            .count()
        )
        return div_tie_count

    @property
    def conf_wins(self):
        conf_win_count = (
            Matchup.objects.completed_for_season_by_team_in_conf(self.season, self.team)
            .home_or_away_wins(self.team)
            .count()
        )
        return conf_win_count

    @property
    def conf_losses(self):
        conf_loss_count = (
            Matchup.objects.completed_for_season_by_team_in_conf(self.season, self.team)
            .home_or_away_losses(self.team)
            .count()
        )
        return conf_loss_count

    @property
    def conf_ties(self):
        conf_tie_count = (
            Matchup.objects.completed_for_season_by_team_in_conf(self.season, self.team)
            .home_or_away_ties()
            .count()
        )
        return conf_tie_count

    @property
    def non_conf_wins(self):
        non_conf_win_count = (
            Matchup.objects.completed_for_season_by_team_non_conf(
                self.season, self.team
            )
            .home_or_away_wins(self.team)
            .count()
        )
        return non_conf_win_count

    @property
    def non_conf_losses(self):
        non_conf_loss_count = (
            Matchup.objects.completed_for_season_by_team_non_conf(
                self.season, self.team
            )
            .home_or_away_losses(self.team)
            .count()
        )
        return non_conf_loss_count

    @property
    def non_conf_ties(self):
        non_conf_tie_count = (
            Matchup.objects.completed_for_season_by_team_non_conf(
                self.season, self.team
            )
            .home_or_away_ties()
            .count()
        )
        return non_conf_tie_count

    @property
    def last_5_wins(self):
        last_5 = Matchup.objects.last_5(self.season, self.team)
        last_5_win_count = (
            Matchup.objects.in_last_5(last_5).home_or_away_wins(self.team).count()
        )
        return last_5_win_count

    @property
    def last_5_losses(self):
        last_5 = Matchup.objects.last_5(self.season, self.team)
        last_5_loss_count = (
            Matchup.objects.in_last_5(last_5).home_or_away_losses(self.team).count()
        )
        return last_5_loss_count

    @property
    def last_5_ties(self):
        last_5 = Matchup.objects.last_5(self.season, self.team)
        last_5_tie_count = Matchup.objects.in_last_5(last_5).home_or_away_ties().count()
        return last_5_tie_count
