import random
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .managers import MatchupManager


class Matchup(models.Model):
    home_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="home_matchups",
    )
    away_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="away_matchups",
    )
    season = models.ForeignKey(
        "seasons.Season",
        on_delete=models.CASCADE,
        related_name="matchups",
    )
    date = models.DateField(default=date(date.today().year, 8, 29))
    week_number = models.PositiveSmallIntegerField(default=1)
    is_postseason = models.BooleanField(default=False)
    is_divisional = models.BooleanField(default=False)
    is_conference = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    objects = MatchupManager()

    def __str__(self):
        return (
            f"{self.away_team.abbreviation} @ {self.home_team.abbreviation}"
            f" - Week {self.week_number} - {self.season}"
        )

    def get_absolute_url(self):
        return reverse(
            "matchups:matchup_detail", args=[self.season.league.slug, self.slug]
        )


class PlayerMatchStat(models.Model):
    player = models.ForeignKey(
        "personnel.Player",
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


class Scoreboard(models.Model):
    """
    Add game clock (countdown will happen in JS
        then update the DB after every play)
    Separate PossessionFieldPosition model for
        down, distance, field position, etc.?
    """

    matchup = models.OneToOneField(Matchup, on_delete=models.CASCADE)
    home_score = models.PositiveSmallIntegerField(default=0)
    away_score = models.PositiveSmallIntegerField(default=0)
    is_final = models.BooleanField(default=False)
    quarter = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    home_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    away_timeouts = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)]
    )

    def __str__(self):
        return f"Scoreboard - {self.matchup}"

    def get_score(self):
        """Obtain match score based on random dice rolls"""
        if not self.is_final:
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

        return {"Home": self.home_score, "Away": self.away_score}

    def get_winner(self):
        """Determine match winner based on final score"""
        if self.home_score > self.away_score:
            return self.matchup.home_team
        elif self.away_score > self.home_score:
            return self.matchup.away_team
        else:
            return "Tie"
