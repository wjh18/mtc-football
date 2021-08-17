from django.contrib import admin

from .models import League


class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "commissioner", "commissioner_name", "creation_date",)
    readonly_fields = ('id',)

admin.site.register(League, LeagueAdmin)
