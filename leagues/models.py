import uuid
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from .utils import (
    get_conference_data,
    get_division_data,
    read_team_info_from_csv,
    generate_player_attributes,
)


class League(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=300)
    gm_name = models.CharField(max_length=300)
    creation_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):

        # True if no instance exists, false if editing existing instance
        no_instance_exists = self._state.adding

        # Save League instance before referencing it for Team creation
        super().save(*args, **kwargs)

        # Only perform if instance doesn't exist yet (initial save)
        if no_instance_exists:
            # Get conference and division data and create them
            conferences = get_conference_data()
            divisions = get_division_data()
            Conference.objects.bulk_create([Conference(league=self, **c) for c in conferences])
            afc = Conference.objects.get(name='AFC', league=self)
            nfc = Conference.objects.get(name='NFC', league=self)
            for division in divisions:
                division_name = division['name']
                if division_name[:3] == 'AFC':
                    Division.objects.create(conference=afc, **division)
                elif division_name[:3] == 'NFC':
                    Division.objects.create(conference=nfc, **division)
            # Read team data from CSV and create 32 teams in League
            team_info = read_team_info_from_csv()
            abbreviations = [*team_info.keys()]
            other_team_info = [*team_info.values()]
            for team in range(0, 32):
                team_conference = Conference.objects.get(
                    name=other_team_info[team][2], league=self
                )
                team_division = Division.objects.get(
                    name=other_team_info[team][3], conference=team_conference
                )
                Team.objects.create(
                    location=other_team_info[team][0],
                    name=other_team_info[team][1],
                    abbreviation=abbreviations[team],
                    division=team_division,
                    league=self)
            # Create first season in league automatically
            Season.objects.create(
                league=self
            )

    def get_absolute_url(self):
        return reverse("league_detail", args=[str(self.id)])


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
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='teams',
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE,
        related_name='teams', default=None
    )
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)

    class Meta:
        ordering = ['location']

    def __str__(self):
        return f'{self.location} {self.name}'

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
                p = Player.objects.create(
                        league=self.league,
                        **player
                    )
                p.team.add(self)

    def calc_team_overall(self):
        team_overall = 0
        for contract in self.contracts.all():
            player = contract.player
            team_overall += player.overall_rating
        team_overall /= 53

        return int(team_overall)

    def get_absolute_url(self):
        return reverse("team_detail", args=[str(self.id)])


class UserTeam(models.Model):
    league = models.OneToOneField(
        League, on_delete=models.CASCADE,
        blank=True, null=True
    )
    team = models.OneToOneField(
        Team, on_delete=models.CASCADE
    )
    is_active_team = models.BooleanField(default=True)


class Person(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
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

    def __str__(self):
        return f'{self.first_name} ' + f' {self.last_name}'


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
    league = models.ForeignKey(
        League, on_delete=models.CASCADE,
        related_name='seasons',
    )
    start_date = models.DateField(default=datetime.date(2021, 8, 29))
    current_date = models.DateField(default=datetime.date(2021, 8, 29))
    duration = models.DurationField(default=datetime.timedelta(weeks=52))
    phase = models.PositiveSmallIntegerField(default=1)
    season_number = models.PositiveSmallIntegerField(default=1)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f'Season {str(self.pk)} - {self.league.name}'


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
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE,
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

    def __str__(self):
        return f'Single Statline for {self.player.first_name} ' + f'{self.player.last_name}'