from django.contrib import admin

from .models import Matchup, PlayerMatchStat, Scoreboard

admin.site.register(Matchup)
admin.site.register(PlayerMatchStat)
admin.site.register(Scoreboard)
