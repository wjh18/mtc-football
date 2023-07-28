from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .models import League


class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for verifying user league ownership in class-based views.
    """

    def test_func(self):
        if self.kwargs.get("league"):
            try:
                league = League.objects.get(slug=self.kwargs["league"])
            except ObjectDoesNotExist:
                return False
            return self.request.user == league.user
        else:
            # Fallback for generic views where league kwarg is 'object'
            return self.request.user == self.get_object().user


def is_league_owner(func):
    """
    Decorator permission for function-based views that verifies
    whether the user is the league owner.
    """

    def wrap(request, *args, **kwargs):
        league = League.objects.get(slug=kwargs["league"])
        if league.user == request.user:
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap
