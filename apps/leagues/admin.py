from django.contrib import admin

from .models import Conference, Division, League


class ConferenceInline(admin.TabularInline):
    model = Conference


class LeagueAdmin(admin.ModelAdmin):
    inlines = [ConferenceInline]
    list_display = (
        "name",
        "user",
        "gm_name",
        "creation_date",
        "slug",
    )
    readonly_fields = ("id",)


class DivisionInline(admin.TabularInline):
    model = Division


class ConferenceAdmin(admin.ModelAdmin):
    inlines = [
        DivisionInline,
    ]
    list_display = (
        "__str__",
        "league",
    )
    readonly_fields = ("id",)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "conference", "get_league")
    readonly_fields = ("id",)


admin.site.register(League, LeagueAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Division, DivisionAdmin)
