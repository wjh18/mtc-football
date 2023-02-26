from django.views.generic.base import ContextMixin

from .models import Team


class TeamsContextMixin(ContextMixin):
    """
    Mixin for accessing a league's teams in context data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league_slug = self.kwargs["league"]
        context["team_list"] = Team.objects.filter(league__slug=league_slug)
        return context
