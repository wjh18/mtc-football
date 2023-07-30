from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import League


class IsLeagueOwner(LoginRequiredMixin, UserPassesTestMixin):
    """
    Permission that verifies a user's league ownership in class-based views.
    """

    def test_func(self):
        league_slug = self.kwargs.get("league")
        if league_slug is not None:
            league = get_object_or_404(League, slug=league_slug)
        else:
            return False
        return self.request.user == league.user


@login_required
def is_league_owner(func):
    """
    Permission that verifies a user's league ownership in function-based views.
    """

    def wrap(request, *args, **kwargs):
        league_slug = kwargs.get("league")
        if league_slug is not None:
            league = get_object_or_404(League, slug=league_slug)
            if league.user == request.user:
                return func(request, *args, **kwargs)
        raise PermissionDenied

    return wrap
