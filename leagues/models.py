import uuid
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