from django.contrib import admin

from .models import Matchup, PlayerMatchStat


class MatchupAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "away_team",
        "home_team",
        "season",
        "date",
        "week_number",
        "slug",
        "home_score",
        "away_score",
        "is_final",
        "quarter",
        "home_timeouts",
        "away_timeouts",
    )
    readonly_fields = ("id",)


class PlayerMatchStatAdmin(admin.ModelAdmin):
    list_display = ("__str__", "player", "matchup")


admin.site.register(Matchup, MatchupAdmin)
admin.site.register(PlayerMatchStat, PlayerMatchStatAdmin)
