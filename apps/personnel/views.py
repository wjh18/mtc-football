from django.views.generic import DetailView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import LeagueOwnerMixin

from .models import Player


class PlayerDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual player in a league.
    """

    model = Player
    context_object_name = "player"
    template_name = "personnel/player_detail.html"
