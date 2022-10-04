from django.contrib import admin

from apps.personnel.admin import PlayerInline

from .models import Team, UserTeam


class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ("__str__", "abbreviation", "league", "division")
    list_filter = ("league__name",)


admin.site.register(Team, TeamAdmin)
admin.site.register(UserTeam)
