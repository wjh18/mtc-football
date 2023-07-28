from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import ContextMixin

from .models import League
from .permissions import LeagueOwnerMixin


class LeagueOwnerRequiredMixin(LoginRequiredMixin):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(user=self.request.user)


class LeagueContextMixin(ContextMixin):
    """
    Mixin for reducing duplicate get_context_data calls for league data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get("league"):
            league = League.objects.get(slug=self.kwargs["league"])
        else:
            # Fallback for generic views where league kwarg is 'object'
            league = self.object

        context["league"] = league
        Season = apps.get_model("seasons.Season")
        context["season"] = Season.objects.get(league=league, is_current=True)

        if self.kwargs.get("team"):
            team_slug = self.kwargs["team"]
            Team = apps.get_model("teams.Team")
            context["team"] = Team.objects.get(league=league, slug=team_slug)

        return context


class LeagueOwnerContextMixin(LeagueOwnerMixin, LeagueContextMixin):
    """Combines 2 mixins commonly used together into 1 class."""

    pass
