from django.contrib import admin

from .models import Matchup, PlayerMatchStat, Scoreboard


class MatchupAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "home_team",
        "away_team",
        "season",
        "date",
        "week_number",
        "is_postseason",
        "is_divisional",
        "is_conference",
        "slug",
    )
    readonly_fields = ("id",)


class PlayerMatchStatAdmin(admin.ModelAdmin):
    list_display = ("__str__", "player", "matchup")


class ScoreboardAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "home_score",
        "away_score",
        "is_final",
        "quarter",
        "home_timeouts",
        "away_timeouts",
    )


admin.site.register(Matchup, MatchupAdmin)
admin.site.register(PlayerMatchStat, PlayerMatchStatAdmin)
admin.site.register(Scoreboard, ScoreboardAdmin)
