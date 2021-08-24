import uuid
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from .utils import (
    read_team_info_from_csv,
    read_player_names_from_csv,
    generate_player_attributes,
)


class League(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=300)
    gm_name = models.CharField(max_length=300)
    creation_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding

        # Save League instance before referencing it for Team creation
        super().save(*args, **kwargs)

        # Read team data from CSV and create 32 teams in League
        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            team_info = read_team_info_from_csv()
            abbreviations = [*team_info.keys()]
            locations_and_names = [*team_info.values()]
            for team in range(0, 32):
                Team.objects.create(
                    location=locations_and_names[team][0],
                    name=locations_and_names[team][1],
                    abbreviation=abbreviations[team],
                    league=self)

    def get_absolute_url(self):
        return reverse("league_detail", args=[str(self.id)])
    

class Team(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='teams',
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['location']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding

        # Save Team instance before referencing it for Player creation
        super().save(*args, **kwargs)

        # Read player names from CSV, generate attributes and create players
        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            player_attributes = generate_player_attributes()
            for player in player_attributes:
                Player.objects.create(
                    team=self,
                    league=self.league,
                    **player)

    def calc_team_overall(self):
        team_overall = 0
        for player in self.players.all():
            team_overall += player.overall_rating
        team_overall /= 53

        return int(team_overall)

    def get_absolute_url(self):
        return reverse("team_detail", args=[str(self.id)])
    

class Person(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
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
    team = models.ForeignKey(
        Team, blank=True, null=True,
        on_delete=models.CASCADE, related_name='players'
    )
    league = models.ForeignKey(
        League, blank=True, null=True,
        on_delete=models.CASCADE, related_name='players'
    )

    class Meta:
        abstract = True


class Player(Person):
    position = models.CharField(default='QB', max_length=50)
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

    def __str__(self):
        return f'{self.first_name}' + '.' + f' {self.last_name}'


class Season(models.Model):
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='seasons',
    )
    start_date = models.DateField(default=datetime.date(2021, 8, 29))
    duration = models.DurationField(default=datetime.timedelta(weeks=52))
    phase = models.PositiveSmallIntegerField(default=1)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f'Season #{str(self.pk)} - {self.league.name}'


class Match(models.Model):
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='home_matches',
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='away_matches',
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE,
        related_name='matches',
    )
    
    def __str__(self):
        return f'Season #{str(self.season.pk)} - {self.home_team} vs. {self.away_team}'


class PlayerStats(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE,
        related_name='player_stats',
    )
    # Passing Offense
    passing_comps = models.IntegerField(default=0)
    passing_atts = models.IntegerField(default=0)
    passing_yds = models.IntegerField(default=0)
    passing_tds = models.IntegerField(default=0)
    passing_ints = models.IntegerField(default=0)
    passing_fds = models.IntegerField(default=0)
    times_sacked = models.IntegerField(default=0)
    # Rushing Offense
    rushing_atts = models.IntegerField(default=0)
    rushing_yds = models.IntegerField(default=0)
    rushing_tds = models.IntegerField(default=0)
    rushing_fds = models.IntegerField(default=0)
    fumbles_lost = models.IntegerField(default=0)
    # Defensive
    def_ints = models.IntegerField(default=0)
    forced_fumbles = models.IntegerField(default=0)
    def_tds = models.IntegerField(default=0)
    def_return_yds = models.IntegerField(default=0)
    tackles = models.IntegerField(default=0)
    tackles_for_loss = models.IntegerField(default=0)
    qb_hits = models.IntegerField(default=0)
    sacks = models.IntegerField(default=0)
    safeties = models.IntegerField(default=0)
    # Kicker Scoring
    field_goals = models.IntegerField(default=0)
    field_goal_atts = models.IntegerField(default=0)
    field_goal_long = models.IntegerField(default=0)
    extra_points = models.IntegerField(default=0)
    extra_point_atts = models.IntegerField(default=0)
    # Kicking & Punting
    kickoffs = models.IntegerField(default=0)
    kickoff_yds = models.IntegerField(default=0)
    touchbacks = models.IntegerField(default=0)
    punts = models.IntegerField(default=0)
    punt_yds = models.IntegerField(default=0)
    punt_long = models.IntegerField(default=0)
    punt_blocks = models.IntegerField(default=0)
    # Returning
    punt_returns = models.IntegerField(default=0)
    punt_return_yds = models.IntegerField(default=0)
    punt_return_tds = models.IntegerField(default=0)
    punt_return_long = models.IntegerField(default=0)
    kick_returns = models.IntegerField(default=0)
    kick_return_yds = models.IntegerField(default=0)
    kick_return_tds = models.IntegerField(default=0)
    kick_return_long = models.IntegerField(default=0)
    # Penalties
    penalties = models.IntegerField(default=0)
    penalty_yds = models.IntegerField(default=0)