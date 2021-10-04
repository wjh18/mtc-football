from django.contrib import admin

from .models import (
    League, Conference, Division,
    UserTeam, Team, Player, Contract,
    Season, Matchup, PlayerMatchStat,
    TeamStanding, TeamRanking,)


class ConferenceInline(admin.TabularInline):
    model = Conference


class LeagueAdmin(admin.ModelAdmin):
    inlines = [
        ConferenceInline
    ]
    list_display = ("name", "user", "gm_name", "creation_date",)
    readonly_fields = ('id',)


class DivisionInline(admin.TabularInline):
    model = Division


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [
        DivisionInline,
    ]
    list_display = ('__str__', 'league')
    readonly_fields = ('id',)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "conference")
    readonly_fields = ('id',)


class PlayerInline(admin.TabularInline):
    """
    Used to show contracts on both Team Admin and Player Admin
    """
    model = Player.team.through
    fields = ('player', 'is_active',)
    readonly_fields = ('player',)
    extra = 0


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline
    ]
    list_display = ('__str__', 'abbreviation', 'league', 'division')
    list_filter = ('league__name',)


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline
    ]
    list_display = ('__str__', 'position', 'prototype',
                    'overall_rating', 'league')
    list_filter = ('team__league__name',)
    search_fields = ('first_name',)


admin.site.register(League, LeagueAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(UserTeam)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Contract)
admin.site.register(Season)
admin.site.register(Matchup)
admin.site.register(PlayerMatchStat)
admin.site.register(TeamStanding)
admin.site.register(TeamRanking)
