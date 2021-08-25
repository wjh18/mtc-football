from django.db import models


class Scoreboard(models.Model):
    matchup = models.OneToOneField(
        'leagues.Matchup', on_delete=models.CASCADE
    )
