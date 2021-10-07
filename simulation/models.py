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
    is_final = models.BooleanField(default=False)
    quarter = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    home_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)])
    away_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)])

    def __str__(self):
        return f'Scoreboard for {self.matchup}'

    def get_score(self):
        """Obtain match score based on random dice rolls"""
        self.home_score = random.randint(0, 50)
        self.away_score = random.randint(0, 50)
        
        # If postseason and a tie, break it with an "overtime" roll
        if self.matchup.is_postseason and self.home_score == self.away_score:
            overtime_pts = random.choice([self.home_score, self.away_score])
            if overtime_pts == self.home_score:
                self.home_score += random.randint(3, 7)
            else:
                self.away_score += random.randint(3, 7)
            
        self.is_final = True
        self.save()

        return {'Home': self.home_score, 'Away': self.away_score}

    def get_winner(self):
        """Determine match winner based on final score"""
        if self.home_score > self.away_score:
            return self.matchup.home_team
        elif self.away_score > self.home_score:
            return self.matchup.away_team
        else:
            return "Tie"
