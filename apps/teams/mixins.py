from django.views.generic.base import ContextMixin


class LeagueTeamsMixin(ContextMixin):
    """
    Mixin for Team views to filter teams by league.
    """

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(league__slug=self.kwargs["league"])
