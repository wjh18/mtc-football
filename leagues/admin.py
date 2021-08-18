from django.contrib import admin

from .models import League, Team


class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "commissioner", "commissioner_name", "creation_date",)
    readonly_fields = ('id',)


class TeamAdmin(admin.ModelAdmin):
    list_display = ("location", "name", "abbreviation")
    readonly_fields = ('id',)

admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
