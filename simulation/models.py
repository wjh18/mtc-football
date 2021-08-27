from django.db import models
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


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
        return f'Scoreboard for Match {str(self.matchup.pk)} Season {str(self.matchup.season.pk)} - {self.matchup.season.league.name}'

    def get_winner(self):
        if home_score > away_score:
            return self.matchup.home_team
        elif away_score > home_score:
            return self.matchup.away_team
        else:
            return "Tie"
