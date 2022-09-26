import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .utils.players import create_team_players
from .utils.setup import create_league_structure, create_season_details
from .utils.text import random_string_generator as random_string


class League(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="leagues"
    )
    name = models.CharField(max_length=50)
    gm_name = models.CharField(max_length=50)
    creation_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # Generate a unique slug
        if not self.slug:
            self.slug = slugify(self.name + "-" + random_string())
        # False if saving an existing instance
        no_instance_exists = self._state.adding
        # Save League instance before creating its structure
        super().save(*args, **kwargs)
        # Only create structure on initial save() call
        if no_instance_exists:
            create_league_structure(self)

    def get_absolute_url(self):
        return reverse("leagues:league_detail", args=[self.slug])


class Conference(models.Model):
    name = models.CharField(max_length=50)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="conferences"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.league}"


class Division(models.Model):
    name = models.CharField(max_length=200)
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="divisions"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.conference.league}"


class Team(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    division = models.ForeignKey(
        Division,
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
        player_ratings = [
            contract.player.overall_rating for contract in self.contracts.all()
        ]
        team_overall = int(sum(player_ratings) / 53)
        self.overall_rating = team_overall
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
        season = Season.objects.get(league=self.league, is_current=True)

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        standing = TeamStanding.objects.get(
            team=self, season=season, week_number=week_number
        )
        return f"({standing.wins}-{standing.losses}-{standing.ties})"

    def get_absolute_url(self):
        return reverse("leagues:team_detail", args=[self.league.slug, self.slug])


class UserTeam(models.Model):
    league = models.OneToOneField(
        League,
        on_delete=models.CASCADE,
    )
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    is_active_team = models.BooleanField(default=True)

    def __str__(self):
        return f"User team - {self.team.abbreviation} - {self.league}"


class Person(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="players")
    team = models.ManyToManyField(Team, through="Contract")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveSmallIntegerField()
    experience = models.PositiveSmallIntegerField()
    prototype = models.CharField(max_length=50)
    overall_rating = models.PositiveSmallIntegerField()
    potential = models.PositiveSmallIntegerField()
    confidence = models.PositiveSmallIntegerField()
    iq = models.PositiveSmallIntegerField()
    is_free_agent = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Player(Person):
    position = models.CharField(max_length=50)
    speed = models.PositiveSmallIntegerField()
    strength = models.PositiveSmallIntegerField()
    agility = models.PositiveSmallIntegerField()
    awareness = models.PositiveSmallIntegerField()
    stamina = models.PositiveSmallIntegerField()
    injury = models.PositiveSmallIntegerField()
    run_off = models.PositiveSmallIntegerField()
    pass_off = models.PositiveSmallIntegerField()
    special_off = models.PositiveSmallIntegerField()
    run_def = models.PositiveSmallIntegerField()
    pass_def = models.PositiveSmallIntegerField()
    special_def = models.PositiveSmallIntegerField()
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Find a way to pass team slug despite ManyToMany
    # def get_absolute_url(self):
    #     # self.league.teams.all()
    #     return reverse("leagues:player_detail",
    #                     args=[self.league, self.contract.team.slug,
    #                           self.slug])


class Contract(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="contracts")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"""{self.player} contract -
                 {self.team.abbreviation} - {self.team.league}"""


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
        League,
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


class Matchup(models.Model):
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_matchups",
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_matchups",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="matchups",
    )
    date = models.DateField(default=datetime.date(2021, 8, 29))
    week_number = models.PositiveSmallIntegerField(default=1)
    is_postseason = models.BooleanField(default=False)
    is_divisional = models.BooleanField(default=False)
    is_conference = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"""{self.away_team.abbreviation} @ {self.home_team.abbreviation}
                - Week {self.week_number} - {self.season}"""

    def get_absolute_url(self):
        return reverse(
            "leagues:matchup_detail", args=[self.season.league.slug, self.slug]
        )


class PlayerMatchStat(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="player_stats",
    )
    matchup = models.ForeignKey(
        Matchup,
        on_delete=models.CASCADE,
        related_name="player_stats",
    )
    # Passing offense
    passing_comps = models.SmallIntegerField(default=0)
    passing_atts = models.SmallIntegerField(default=0)
    passing_yds = models.SmallIntegerField(default=0)
    passing_tds = models.SmallIntegerField(default=0)
    passing_ints = models.SmallIntegerField(default=0)
    passing_fds = models.SmallIntegerField(default=0)
    times_sacked = models.SmallIntegerField(default=0)
    # Receiving offense
    receptions = models.SmallIntegerField(default=0)
    receiving_targets = models.SmallIntegerField(default=0)
    receiving_yds = models.SmallIntegerField(default=0)
    receiving_tds = models.SmallIntegerField(default=0)
    receiving_fds = models.SmallIntegerField(default=0)
    # Rushing offense
    rushing_atts = models.SmallIntegerField(default=0)
    rushing_yds = models.SmallIntegerField(default=0)
    rushing_tds = models.SmallIntegerField(default=0)
    rushing_fds = models.SmallIntegerField(default=0)
    fumbles_lost = models.SmallIntegerField(default=0)
    # Defensive
    def_ints = models.SmallIntegerField(default=0)
    forced_fumbles = models.SmallIntegerField(default=0)
    def_tds = models.SmallIntegerField(default=0)
    def_return_yds = models.SmallIntegerField(default=0)
    tackles = models.SmallIntegerField(default=0)
    tackles_for_loss = models.SmallIntegerField(default=0)
    qb_hits = models.SmallIntegerField(default=0)
    sacks = models.SmallIntegerField(default=0)
    safeties = models.SmallIntegerField(default=0)
    # Kicker scoring
    field_goals = models.SmallIntegerField(default=0)
    field_goal_atts = models.SmallIntegerField(default=0)
    field_goal_long = models.SmallIntegerField(default=0)
    extra_points = models.SmallIntegerField(default=0)
    extra_point_atts = models.SmallIntegerField(default=0)
    # Kicking and punting
    kickoffs = models.SmallIntegerField(default=0)
    kickoff_yds = models.SmallIntegerField(default=0)
    touchbacks = models.SmallIntegerField(default=0)
    punts = models.SmallIntegerField(default=0)
    punt_yds = models.SmallIntegerField(default=0)
    punt_long = models.SmallIntegerField(default=0)
    punt_blocks = models.SmallIntegerField(default=0)
    # Returning
    punt_returns = models.SmallIntegerField(default=0)
    punt_return_yds = models.SmallIntegerField(default=0)
    punt_return_tds = models.SmallIntegerField(default=0)
    punt_return_long = models.SmallIntegerField(default=0)
    kick_returns = models.SmallIntegerField(default=0)
    kick_return_yds = models.SmallIntegerField(default=0)
    kick_return_tds = models.SmallIntegerField(default=0)
    kick_return_long = models.SmallIntegerField(default=0)
    # Penalties
    penalties = models.SmallIntegerField(default=0)
    penalty_yds = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.player} stats - {self.matchup}"


class TeamStanding(models.Model):
    team = models.ForeignKey(
        Team,
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
