from django.db import models


class MatchupManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "home_team__league",
                "home_team__conference",
                "home_team__division",
                "away_team__league",
                "away_team__conference",
                "away_team__division",
                "scoreboard",
                "season__league",
            )
        )
