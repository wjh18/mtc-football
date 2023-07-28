from django.apps import apps
from django.http import Http404
from django.views.generic import DetailView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import IsLeagueOwner

from .models import Matchup


class WeeklyMatchupsView(IsLeagueOwner, LeagueContextMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/matchups.html"

    def get_queryset(self):
        season = self.get_season()
        week_number = self.get_week_number(season)

        matchups = Matchup.objects.with_extras().filter(
            season=season, week_number=week_number
        )

        return matchups

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        season = self.get_season()
        week_number = self.get_week_number(season)

        context["week_num"] = week_number
        context["num_weeks"] = range(1, 23)

        if 6 <= week_number <= 13:
            context["bye_teams"] = season.get_byes(week_number)

        return context

    def get_season(self):
        League = apps.get_model("leagues.League")
        Season = apps.get_model("seasons.Season")
        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)
        return season

    def get_week_number(self, season):
        week_kw = self.kwargs.get("week_num", False)
        weeks = range(1, 23)

        # Only accept valid week parameters in URL
        if season.week_number == 23 and not week_kw:
            week_number = season.week_number - 1
        elif week_kw and (week_kw not in weeks or week_kw == 0):
            raise Http404("Invalid week number supplied")
        elif not week_kw:
            week_number = season.week_number
        else:
            week_number = self.kwargs["week_num"]

        return week_number


class MatchupDetailView(IsLeagueOwner, LeagueContextMixin, DetailView):
    """
    View additional details related to an individual matchup.
    """

    model = Matchup
    context_object_name = "matchup"
    template_name = "matchups/matchup_detail.html"

    def get_queryset(self):
        League = apps.get_model("leagues.League")
        league = League.objects.get(slug=self.kwargs["league"])
        return Matchup.objects.with_extras().filter(season__league=league)


class PlayoffsView(IsLeagueOwner, LeagueContextMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/playoffs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        matchups = Matchup.objects.with_extras().filter(
            season=context["season"], week_number__gte=19
        )
        context["wildcard_matchups"] = matchups.filter(week_number=19)
        context["divisional_matchups"] = matchups.filter(week_number=20)
        context["conference_matchups"] = matchups.filter(week_number=21)
        context["championship_matchups"] = matchups.filter(week_number=22)

        return context
