import datetime

from django.db import models

from .setup import create_season_details


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
    start_date = models.DateField(default=datetime.date(2021, 8, 29))
    current_date = models.DateField(default=datetime.date(2021, 8, 29))
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
        if not week_num:
            week_number = self.week_number
        else:
            week_number = week_num

        matchups = self.matchups.filter(week_number=week_number)
        teams_in_league = {team for team in self.league.teams.all()}
        teams_playing_this_week = set()

        for matchup in matchups:
            teams_playing_this_week.add(matchup.home_team)
            teams_playing_this_week.add(matchup.away_team)

        teams_with_bye = teams_in_league - teams_playing_this_week
        return teams_with_bye


class TeamStanding(models.Model):
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
    week_number = models.PositiveSmallIntegerField(default=1)
    # Basic standings
    wins = models.SmallIntegerField(default=0)
    losses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    points_for = models.SmallIntegerField(default=0)
    points_against = models.SmallIntegerField(default=0)
    streak = models.SmallIntegerField(default=0)
    # Home and away records
    home_wins = models.SmallIntegerField(default=0)
    home_losses = models.SmallIntegerField(default=0)
    home_ties = models.SmallIntegerField(default=0)
    away_wins = models.SmallIntegerField(default=0)
    away_losses = models.SmallIntegerField(default=0)
    away_ties = models.SmallIntegerField(default=0)
    # Division, conference, and non-conf records
    div_wins = models.SmallIntegerField(default=0)
    div_losses = models.SmallIntegerField(default=0)
    div_ties = models.SmallIntegerField(default=0)
    conf_wins = models.SmallIntegerField(default=0)
    conf_losses = models.SmallIntegerField(default=0)
    conf_ties = models.SmallIntegerField(default=0)
    non_conf_wins = models.SmallIntegerField(default=0)
    non_conf_losses = models.SmallIntegerField(default=0)
    non_conf_ties = models.SmallIntegerField(default=0)
    # Record for last 5 games
    last_5_wins = models.SmallIntegerField(default=0)
    last_5_losses = models.SmallIntegerField(default=0)
    last_5_ties = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"""{self.team.abbreviation} standings -
                Week {self.week_number} - {self.season}"""


class TeamRanking(models.Model):
    standing = models.OneToOneField(
        TeamStanding,
        related_name="ranking",
        on_delete=models.CASCADE,
    )
    # Regular season
    division_ranking = models.PositiveSmallIntegerField(default=1)
    conference_ranking = models.PositiveSmallIntegerField(default=1)
    power_ranking = models.PositiveSmallIntegerField(default=1)
    # Postseason clinches
    clinch_bye = models.BooleanField(default=False)
    clinch_div = models.BooleanField(default=False)
    clinch_berth = models.BooleanField(default=False)
    clinch_none = models.BooleanField(default=False)
    # Postseason advancement
    won_wild = models.BooleanField(default=False)
    won_div = models.BooleanField(default=False)
    won_conf = models.BooleanField(default=False)
    won_champ = models.BooleanField(default=False)

    def __str__(self):
        return f"""{self.standing.team.abbreviation} rankings -
                Week {self.standing.week_number} -
                {self.standing.season}"""
