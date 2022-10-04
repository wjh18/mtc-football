from django.contrib import admin

from .models import Season, TeamRanking, TeamStanding

admin.site.register(Season)
admin.site.register(TeamStanding)
admin.site.register(TeamRanking)
