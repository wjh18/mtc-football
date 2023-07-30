from __future__ import annotations

import random
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.teams.models import Team

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from .exceptions import MatchFinalizedError, MatchInProgressError
from .managers import MatchupManager, MatchupQuerySet


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
    slug = models.SlugField(max_length=255, blank=True, null=True)
    # Scoreboard fields
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

    objects = MatchupManager.from_queryset(MatchupQuerySet)()

    def __str__(self):
        return f"{self.away_team.abbreviation} @ {self.home_team.abbreviation}"

    def get_absolute_url(self):
        return reverse(
            "matchups:matchup_detail", args=[self.season.league.slug, self.slug]
        )

    @cached_property
    def is_postseason(self) -> bool:
        return self.week_number >= 19

    @cached_property
    def is_divisional(self) -> bool:
        return self.home_team.division == self.away_team.division

    @cached_property
    def is_conference(self) -> bool:
        return self.home_team.conference == self.away_team.conference

    def simulate(self):
        """
        Simulate the match based on random dice rolls.

        This will be updated in the future to add in additional complexity
        by taking into account team/player strength and scenario-based results.
        """
        if self.is_final:
            raise MatchFinalizedError(
                "Unable to simulate match. Match has been finalized."
            )
        scoreline = self._generate_score()
        valid_score = self._check_impossible_scoreline(scoreline)
        if scoreline != valid_score:
            self.home_score, self.away_score = valid_score

        # If postseason and a tie, break it with a tiebreaker roll
        if self.is_postseason and self.home_score == self.away_score:
            self._tiebreaker()

        self.is_final = True
        self.save()

    def _generate_score(self) -> tuple:
        min_score, max_score = 0, 50
        self.home_score = random.randint(min_score, max_score)
        self.away_score = random.randint(min_score, max_score)
        scoreline = (self.home_score, self.away_score)
        return scoreline

    def _check_impossible_scoreline(self, scoreline: tuple) -> tuple:
        """
        Checks whether the generated scoreline is impossible or not
        and if so, generates a new one.

        Impossible scorelines in American football:
        1-0, 1-1, 2-1, 3-1, 4-1, 5-1, 7-1 (and their inverses)
        6-1 is possible with 1-point safety after an opposing TD (very rare)
        """
        score_1_to_1 = scoreline[0] == 1 and scoreline[1] == 1
        score_1_to_any = 1 in scoreline and any(
            score in scoreline for score in (0, 2, 3, 4, 5, 7)
        )
        impossible_score = score_1_to_1 or score_1_to_any

        if impossible_score:
            # Impossible scoreline based on rules; generate again
            scoreline = self._generate_score()

        return scoreline

    def _tiebreaker(self):
        """Tiebreaker for playoff matches that end in a tie."""
        tiebreak_winner = random.choice((self.home_score, self.away_score))
        add_score = random.choice((3, 7))  # Field goal or TD
        if tiebreak_winner == self.home_score:
            self.home_score += add_score
            return
        self.away_score += add_score

    def get_score(self):
        """Return the current match score, final or not."""
        return {"Home": self.home_score, "Away": self.away_score}

    def get_leading_team(self) -> Team | None:
        """
        Determine the match leader based on current score. Calling on a match
        that's already complete results in an exception.

        Returns:
            The leading team or None if the match is currently tied.
        """
        if not self.is_final:
            return self._get_leading_or_winning_team()
        raise MatchFinalizedError(
            "Unable to determine leading team. Match has been finalized."
        )

    def get_winning_team(self) -> Team | None:
        """
        Determine the match winner based on final score. Calling on a match
        that's still in progress results in an exception.

        Returns:
            The winning team or None if the match resulted in a tie.
        """
        if self.is_final:
            return self._get_leading_or_winning_team()
        raise MatchInProgressError(
            "Unable to determine winning team. Match still in progress."
        )

    def _get_leading_or_winning_team(self) -> Team | None:
        home_score, away_score = self.home_score, self.away_score
        home_team, away_team = self.home_team, self.away_team

        if home_score != away_score:
            return home_team if home_score > away_score else away_team


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
