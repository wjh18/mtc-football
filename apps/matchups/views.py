import copy

from django.views.generic import DetailView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import IsLeagueOwner

from .models import Matchup

WEEK_ROUNDS = {
    19: "Wildcard Weekend",
    20: "Divisional Round",
    21: "Conference Finals",
    22: "Championship",
}


class WeeklyMatchupsView(IsLeagueOwner, LeagueContextMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/matchups.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        season = super().get_context_data(object_list=queryset)["season"]
        week_kw = self.kwargs.get("week_num")
        week_number = season.week_number_from_kwargs(week_kw)
        return queryset.with_cases().filter(season=season, week_number=week_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        season = context["season"]
        week_kw = self.kwargs.get("week_num")
        week_number = season.week_number_from_kwargs(week_kw)

        context["week_num"] = week_number
        context["num_weeks"] = range(1, 23)

        if 6 <= week_number <= 13:
            context["bye_teams"] = season.get_byes(week_number)

        return context


class MatchupDetailView(IsLeagueOwner, LeagueContextMixin, DetailView):
    """
    View additional details related to an individual matchup.
    """

    model = Matchup
    context_object_name = "matchup"
    template_name = "matchups/matchup_detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        league_slug = self.kwargs.get("league")
        if league_slug is not None:
            return queryset.with_cases().filter(season__league__slug=league_slug)
        return queryset


class PlayoffsView(IsLeagueOwner, LeagueContextMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/playoffs.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        season = super().get_context_data(object_list=queryset)["season"]
        return (
            queryset.with_cases()
            .filter(season=season, week_number__gte=19)
            .order_by("week_number")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["week_to_round"] = copy.copy(WEEK_ROUNDS)
        return context
