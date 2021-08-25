from django.contrib import admin

from .models import (
    League, Conference, Division, UserTeam,
    Team, Player, Season, Match, PlayerStats
)


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
    list_display = ('name', 'league')
    readonly_fields = ('id',)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "conference")
    readonly_fields = ('id',)


class PlayerInline(admin.TabularInline):
    model = Player


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline
    ]
    list_display = ('__str__', 'location', 'name', 'abbreviation', 'league',)
    list_filter = ('league',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'first_name', 'last_name', 'team', 'league',)
    list_filter = ('league',)
    search_fields = ('first_name',)

admin.site.register(League, LeagueAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Season)
admin.site.register(Match)
admin.site.register(PlayerStats)
admin.site.register(UserTeam)
