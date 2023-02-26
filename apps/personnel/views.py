from django.views.generic import DetailView

from apps.leagues.mixins import LeagueOwnerContextMixin

from .models import Player


class PlayerDetailView(LeagueOwnerContextMixin, DetailView):
    """
    View additional details about an individual player in a league.
    """

    model = Player
    context_object_name = "player"
    template_name = "personnel/player_detail.html"
