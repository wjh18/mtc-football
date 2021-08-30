from django.db import models
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
import random


class Scoreboard(models.Model):
    """
    Add game clock (countdown will happen in JS
        then update the DB after every play)
    Separate PossessionFieldPosition model for
        down, distance, field position, etc.?
    """
    matchup = models.OneToOneField(
        'leagues.Matchup', on_delete=models.CASCADE
    )
    home_score = models.PositiveSmallIntegerField(default=0)
    away_score = models.PositiveSmallIntegerField(default=0)
    # game_clock =
    quarter = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    home_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)])
    away_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)])
    # home_possession = models.BooleanField()
    # down = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    # distance = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    # field_position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])

    def __str__(self):
        return f'Scoreboard for Match (week {str(self.matchup.week_number)}) Season {str(self.matchup.season.season_number)} - {self.matchup.season.league.name}'

    def get_score(self):
        self.home_score = random.randint(0, 50)
        self.away_score = random.randint(0, 50)
        self.save()

    def get_winner(self):
        if self.home_score > self.away_score:
            return self.matchup.home_team
        elif self.away_score > self.home_score:
            return self.matchup.away_team
        else:
            return "Tie"
