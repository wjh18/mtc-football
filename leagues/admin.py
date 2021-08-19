from django.contrib import admin

from .models import League, Team, Player


class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "commissioner", "commissioner_name", "creation_date",)
    readonly_fields = ('id',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'location', 'name', 'abbreviation', 'league',)
    list_filter = ('league',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'first_name', 'last_name', 'team', 'league',)
    list_filter = ('league',)
    search_fields = ('first_name',)

admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)