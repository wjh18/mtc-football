from django.contrib import admin

from .models import (
    League, Conference, Division, UserTeam,
    Team, Player, Season, Match, PlayerStats
)


class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "gm_name", "creation_date",)
    readonly_fields = ('id',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'location', 'name', 'abbreviation', 'league',)
    list_filter = ('league',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'first_name', 'last_name', 'team', 'league',)
    list_filter = ('league',)
    search_fields = ('first_name',)

admin.site.register(League, LeagueAdmin)
admin.site.register(Conference)
admin.site.register(Division)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Season)
admin.site.register(Match)
admin.site.register(PlayerStats)
admin.site.register(UserTeam)
