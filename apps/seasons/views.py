from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.views.generic import FormView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import IsLeagueOwner

from .forms import AdvanceSeasonForm
from .models import TeamStanding
from .services.season import advance_season_by_weeks


class LeagueStandingsView(IsLeagueOwner, LeagueContextMixin, ListView):
    """
    View team standings by division, conference, or league-wide.
    """

    model = TeamStanding
    context_object_name = "standings"
    # template_name = "seasons/standings2.html"

    def get_template_names(self):
        names = super().get_template_names()
        entity = self.request.GET.get("entity", "division")

        entity_tmpls = {
            "division": "seasons/division_standings.html",
            "conference": "seasons/conference_standings.html",
            "power": "seasons/power_rankings.html",
        }
        try:
            names.append(entity_tmpls[entity])
        except KeyError:
            names.append(entity_tmpls["division"])
        return names

    def get_queryset(self):
        queryset = super().get_queryset()
        season = super().get_context_data(object_list=queryset)["season"]

        queryset = queryset.with_extras().with_wlt().filter(season=season)
        entity = self.request.GET.get("entity", "division")

        entity_qs = {
            "division": queryset.order_by(
                "team__conference",
                "team__division__id",
                "division_ranking",
                "-team__overall_rating",
            ),
            "conference": queryset.order_by(
                "team__conference", "conference_ranking", "-team__overall_rating"
            ),
            "power": queryset.order_by("power_ranking", "-team__overall_rating"),
        }

        try:
            return entity_qs[entity]
        except KeyError:
            raise Http404("Invalid standings entity supplied")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["entity"] = self.request.GET.get("entity", "division")
        return context


class AdvanceSeasonFormView(IsLeagueOwner, LeagueContextMixin, FormView):
    """
    Advance the regular season, playoffs or to the next season
    based on the number of weeks submitted in the form.
    """

    form_class = AdvanceSeasonForm
    template_name = "seasons/forms/advance_season_form.html"

    def post(self, request, *args, **kwargs):
        """
        Override FormView post() method to ensure the user has
        selected a team before advancing the season.
        """
        context = self.get_context_data()
        league = context["league"]

        try:
            league.user_teams.get(is_active_team=True)
        except ObjectDoesNotExist:
            messages.error(request, "Please select a team before advancing.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Get Season context provided by LeagueContextMixin
        context = self.get_context_data()
        season = context["season"]

        # Advance to end of phase or X weeks
        advance = form.cleaned_data["advance"]
        if advance == "Next":
            weeks = False
        else:
            weeks = int(advance)
        advance_season_by_weeks(self.request, season, weeks)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", "/")
