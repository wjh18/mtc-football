from django.views.generic import DetailView

from .models import Player


class PlayerDetailView(DetailView):
    """
    View additional details about an individual player in a league.
    """

    model = Player
    context_object_name = "player"
    template_name = "personnel/player_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(league__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object
        context["team"] = player.current_team
        context["league"] = player.league
        return context
