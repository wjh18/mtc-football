from django.db import models
from django.db.models import Case, Count, F, FloatField, Q, When
from django.db.models.functions import Cast


class TeamStandingManager(models.Manager):
    def get_queryset(self):
        return TeamStandingQuerySet(self.model, using=self._db).select_related(
            "team__league", "team__conference", "team__division"
        )


class TeamStandingQuerySet(models.QuerySet):
    def with_extras(self):
        return self.annotate(
            pt_diff=F("points_for") - F("points_against"),
            win_pct=Case(
                When(
                    wins__gt=0,
                    then=Cast("wins", FloatField())
                    / (F("wins") + F("losses") + F("ties")),
                ),
                default=F("wins"),
                output_field=FloatField(),
            ),
            games_played=F("wins") + F("losses") + F("ties"),
        )

    def with_wlt(self):
        finalized_reg_season = Q(
            season__matchups__season=F("season"),
            season__matchups__is_final=True,
            season__matchups__week_number__lte=18,
        )
        home_team = Q(season__matchups__home_team=F("team"))
        away_team = Q(season__matchups__away_team=F("team"))
        match_participant = home_team | away_team
        home_won_match = Q(
            season__matchups__home_score__gt=F("season__matchups__away_score")
        )
        away_won_match = Q(
            season__matchups__away_score__gt=F("season__matchups__home_score")
        )
        home_win = home_team & home_won_match
        away_win = away_team & away_won_match
        home_loss = home_team & away_won_match
        away_loss = away_team & home_won_match
        win = home_win | away_win
        loss = home_loss | away_loss
        tie = Q(season__matchups__home_score=F("season__matchups__away_score"))
        is_divisional = Q(
            season__matchups__home_team__division=F(
                "season__matchups__away_team__division"
            )
        )
        is_conference = Q(
            season__matchups__home_team__conference=F(
                "season__matchups__away_team__conference"
            )
        )
        last_5 = Q(season__matchups__week_number__gte=F("season__week_number") - 5)

        return self.filter(finalized_reg_season).annotate(
            home_wins=Count("season__matchups", filter=(home_team & home_won_match)),
            home_losses=Count("season__matchups", filter=(home_team & ~home_won_match)),
            home_ties=Count("season__matchups", filter=(home_team & tie)),
            away_wins=Count("season__matchups", filter=(away_team & away_won_match)),
            away_losses=Count("season__matchups", filter=(away_team & ~away_won_match)),
            away_ties=Count("season__matchups", filter=(away_team & tie)),
            div_wins=Count(
                "season__matchups", filter=(match_participant & is_divisional & win)
            ),
            div_losses=Count(
                "season__matchups", filter=(match_participant & is_divisional & loss)
            ),
            div_ties=Count(
                "season__matchups", filter=(match_participant & is_divisional & tie)
            ),
            conf_wins=Count(
                "season__matchups",
                filter=(match_participant & is_conference & ~is_divisional & win),
            ),
            conf_losses=Count(
                "season__matchups",
                filter=(match_participant & is_conference & ~is_divisional & loss),
            ),
            conf_ties=Count(
                "season__matchups",
                filter=(match_participant & is_conference & ~is_divisional & tie),
            ),
            non_conf_wins=Count(
                "season__matchups",
                filter=(match_participant & ~is_conference & ~is_divisional & win),
            ),
            non_conf_losses=Count(
                "season__matchups",
                filter=(match_participant & ~is_conference & ~is_divisional & loss),
            ),
            non_conf_ties=Count(
                "season__matchups",
                filter=(match_participant & ~is_conference & ~is_divisional & tie),
            ),
            last_5_wins=Count(
                "season__matchups", filter=(match_participant & last_5 & win)
            ),
            last_5_losses=Count(
                "season__matchups", filter=(match_participant & last_5 & loss)
            ),
            last_5_ties=Count(
                "season__matchups", filter=(match_participant & last_5 & tie)
            ),
        )
