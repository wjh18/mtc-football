from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.base import ContextMixin

from .models import League


class LeagueOwnerRequiredMixin(LoginRequiredMixin):
    """
    Psuedo-permission for generic League views that only allows a user
    to access League objects that they're the owner of.
    """

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(user=self.request.user)


class LeagueContextMixin(ContextMixin):
    """
    Mixin that adds the League an object or view is associated with
    to the template context. Not for use in generic League views themselves.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        league_slug = self.kwargs.get("league")
        if league_slug is not None:
            league = get_object_or_404(League, slug=league_slug)
        else:
            league = None

        context["league"] = league
        context["season"] = league.current_season

        return context
