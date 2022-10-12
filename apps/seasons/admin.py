from django.contrib import admin

from .models import Season, TeamStanding


class SeasonAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
        "league",
        "phase",
        "week_number",
        "season_number",
        "start_date",
        "current_date",
        "is_current",
    )


class TeamStandingAdmin(admin.ModelAdmin):

    list_display = (
        "team",
        "season",
        "get_league",
        "wins",
        "losses",
        "ties",
        "points_for",
        "points_against",
        "streak",
        "division_ranking",
        "conference_ranking",
        "power_ranking",
        "clinch_bye",
        "clinch_div",
        "clinch_berth",
        "clinch_none",
        "won_wild",
        "won_div",
        "won_conf",
        "won_champ",
    )


admin.site.register(Season, SeasonAdmin)
admin.site.register(TeamStanding, TeamStandingAdmin)
