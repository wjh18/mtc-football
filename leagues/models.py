import datetime
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from .utils.league_setup import (
    create_league_structure,
    create_team_players,
    create_season_details)
from .utils.url_utils import random_string_generator as random_string

class League(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='leagues'
    )
    name = models.CharField(max_length=300)
    gm_name = models.CharField(max_length=300)
    creation_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        # Generate unique slug
        if not self.slug:
            self.slug = slugify(self.name + "-" + random_string())
        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding
        # Save League instance before referencing it for Team creation
        super().save(*args, **kwargs)
        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            create_league_structure(self)

    def get_absolute_url(self):
        return reverse("leagues:league_detail", args=[self.slug])


class Conference(models.Model):
    name = models.CharField(max_length=200)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='conferences'
    )

    def __str__(self):
        return f'{self.name} - {self.league.name}'


class Division(models.Model):
    name = models.CharField(max_length=200)
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE,
        related_name='divisions'
    )

    def __str__(self):
        return f'{self.name} - {self.conference.league.name}'


class Team(models.Model):
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='teams',
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE,
        related_name='teams',
    )
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)
    overall_rating = models.PositiveSmallIntegerField(default=1)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        ordering = ['location']

    def __str__(self):
        return f'{self.location} {self.name} ({self.abbreviation})'

    def save(self, *args, **kwargs):
        # Generate unique slug
        if not self.slug:
            self.slug = self.abbreviation
        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding
        # Save Team instance before referencing it for Player creation
        super().save(*args, **kwargs)
        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            create_team_players(self)

    def update_team_overall(self):
        player_ratings = [
            contract.player.overall_rating for contract in self.contracts.all()
        ]
        team_overall = int(sum(player_ratings) / 53)
        self.overall_rating = team_overall
        self.save()

    def get_absolute_url(self):
        return reverse("leagues:team_detail", args=[self.league.slug, self.slug])


class UserTeam(models.Model):
    league = models.OneToOneField(
        League, on_delete=models.CASCADE,
    )
    team = models.OneToOneField(
        Team, on_delete=models.CASCADE
    )
    is_active_team = models.BooleanField(default=True)

    def __str__(self):
        return f'User team: {self.team.name}'


class Person(models.Model):
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='players'
    )
    team = models.ManyToManyField(
        Team, through='Contract'
    )
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
        return f'{self.first_name} ' + f' {self.last_name}'
    
    def save(self, *args, **kwargs):
        # Generate unique slug
        if not self.slug:
            self.slug = slugify(f'{self.first_name}-{self.last_name}-{random_string()}')
        super().save(*args, **kwargs)

    # Find a way to pass team slug despite ManyToMany
    # def get_absolute_url(self):
    #     # self.league.teams.all()
    #     return reverse("leagues:player_detail", args=[self.league,
    #                                                   self.contract.team.slug, self.slug])


class Contract(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        related_name='contracts',
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='contracts'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.player.first_name} {self.player.last_name} - {self.team.location} {self.team.name} (Contract)'


class Season(models.Model):
    PHASES = (
        (1, 'Re-signing'),
        (2, 'Free Agent Signing'),
        (3, 'Draft'),
        (4, 'Regular Season'),
        (5, 'Playoffs'),
        (6, 'Offseason'),
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='seasons',
    )
    start_date = models.DateField(default=datetime.date(2021, 8, 29))
    current_date = models.DateField(default=datetime.date(2021, 8, 29))
    duration = models.DurationField(default=datetime.timedelta(weeks=52))
    phase = models.PositiveSmallIntegerField(default=4, choices=PHASES)
    season_number = models.PositiveSmallIntegerField(default=1)
    week_number = models.PositiveSmallIntegerField(default=1)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f'Season {str(self.season_number)} - {self.league.name}'

    def save(self, *args, **kwargs):
        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding
        # Save Season instance before referencing it for schedule / Matchup creation
        super().save(*args, **kwargs)        
        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            create_season_details(self)

    def get_byes(self):
        matchups = self.matchups.filter(week_number=self.week_number)
        teams_in_league = {team for team in self.league.teams.all()}
        teams_playing_this_week = set()
        for matchup in matchups:
            teams_playing_this_week.add(matchup.home_team)
            teams_playing_this_week.add(matchup.away_team)
        teams_with_bye = teams_in_league - teams_playing_this_week

        return teams_with_bye


class Matchup(models.Model):
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='home_matchups',
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='away_matchups',
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE,
        related_name='matchups',
    )
    date = models.DateField(default=datetime.date(2021, 8, 29))
    week_number = models.PositiveSmallIntegerField(default=1)
    is_preseason = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return f'Season {str(self.season.season_number)} Week {str(self.week_number)} - {self.home_team} vs. {self.away_team}'
    
    def save(self, *args, **kwargs):
        # Generate unique slug
        if not self.slug:
            self.slug = slugify(
                f'{self.home_team.abbreviation}-{self.away_team.abbreviation}-season-{self.season.season_number}-week-{self.week_number}'
            )
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse("leagues:matchup_detail", args=[self.season.league.slug, self.slug])


class PlayerMatchStat(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    matchup = models.ForeignKey(
        Matchup, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    # Passing Offense
    passing_comps = models.SmallIntegerField(default=0)
    passing_atts = models.SmallIntegerField(default=0)
    passing_yds = models.SmallIntegerField(default=0)
    passing_tds = models.SmallIntegerField(default=0)
    passing_ints = models.SmallIntegerField(default=0)
    passing_fds = models.SmallIntegerField(default=0)
    times_sacked = models.SmallIntegerField(default=0)
    # Receiving Offense
    receptions = models.SmallIntegerField(default=0)
    receiving_targets = models.SmallIntegerField(default=0)
    receiving_yds = models.SmallIntegerField(default=0)
    receiving_tds = models.SmallIntegerField(default=0)
    receiving_fds = models.SmallIntegerField(default=0)
    # Rushing Offense
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
    # Kicker Scoring
    field_goals = models.SmallIntegerField(default=0)
    field_goal_atts = models.SmallIntegerField(default=0)
    field_goal_long = models.SmallIntegerField(default=0)
    extra_points = models.SmallIntegerField(default=0)
    extra_point_atts = models.SmallIntegerField(default=0)
    # Kicking & Punting
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
    penalties = models.IntegerField(default=0)
    penalty_yds = models.IntegerField(default=0)

    def __str__(self):
        return f'Single Statline for {self.player.first_name} ' + f'{self.player.last_name}'


class TeamStanding(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='team_standings',
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE,
        related_name='team_standings',
    )
    week_number = models.PositiveSmallIntegerField(default=1)
    wins = models.SmallIntegerField(default=0)
    losses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    points_for = models.SmallIntegerField(default=0)
    points_against = models.SmallIntegerField(default=0)
    streak = models.SmallIntegerField(default=0)
    home_wins = models.SmallIntegerField(default=0)
    home_losses = models.SmallIntegerField(default=0)
    home_ties = models.SmallIntegerField(default=0)
    away_wins = models.SmallIntegerField(default=0)
    away_losses = models.SmallIntegerField(default=0)
    away_ties = models.SmallIntegerField(default=0)
    div_wins = models.SmallIntegerField(default=0)
    div_losses = models.SmallIntegerField(default=0)
    div_ties = models.SmallIntegerField(default=0)
    conf_wins = models.SmallIntegerField(default=0)
    conf_losses = models.SmallIntegerField(default=0)
    conf_ties = models.SmallIntegerField(default=0)
    non_conf_wins = models.SmallIntegerField(default=0)
    non_conf_losses = models.SmallIntegerField(default=0)
    non_conf_ties = models.SmallIntegerField(default=0)
    last_5_wins = models.SmallIntegerField(default=0)
    last_5_losses = models.SmallIntegerField(default=0)
    last_5_ties = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.team.name} standings for Week {self.week_number} Season {self.season.season_number}'


class TeamRanking(models.Model):
    standing = models.OneToOneField(
        TeamStanding, related_name='ranking',
        on_delete=models.CASCADE,
    )
    power_ranking = models.PositiveSmallIntegerField(default=1)
    conference_ranking = models.PositiveSmallIntegerField(default=1)
    division_ranking = models.PositiveSmallIntegerField(default=1)
    
    def __str__(self):
        return f'Rankings for {self.standing}'