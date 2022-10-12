from django.contrib import admin

from apps.personnel.admin import PlayerInline

from .models import Team, UserTeam


class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ("__str__", "abbreviation", "league", "division", "overall_rating")
    list_filter = ("league__name",)


class UserTeamAdmin(admin.ModelAdmin):
    list_display = ("league", "team", "get_user", "is_active_team")


admin.site.register(Team, TeamAdmin)
admin.site.register(UserTeam, UserTeamAdmin)
