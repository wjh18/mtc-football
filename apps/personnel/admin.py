from django.contrib import admin

from .models import Contract, Player


class PlayerInline(admin.TabularInline):
    """Show contracts on both Team and Player Admin"""

    model = Player.team.through
    fields = (
        "player",
        "team",
        "is_active",
    )
    readonly_fields = ("player",)
    extra = 0


class PlayerAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ("__str__", "position", "prototype", "overall_rating", "league")
    list_filter = ("team__league__name",)
    search_fields = ("first_name",)


class ContractAdmin(admin.ModelAdmin):
    list_display = ("__str__", "player", "team", "get_league")


admin.site.register(Player, PlayerAdmin)
admin.site.register(Contract, ContractAdmin)
