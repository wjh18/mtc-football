from django.apps import apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, F, FloatField, When
from django.db.models.functions import Cast
from django.http import Http404, HttpResponseRedirect
from django.views.generic import FormView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import LeagueOwnerMixin

from .forms import AdvanceSeasonForm
from .models import Season, TeamStanding
from .services.season import advance_season_by_weeks


class LeagueStandingsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View team standings by division, conference, or league-wide.
    """

    model = TeamStanding
    context_object_name = "standings"
    template_name = "seasons/standings.html"

    def get_queryset(self):
        League = apps.get_model("leagues.League")
        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)

        standings = (
            TeamStanding.objects.filter(season=season)
            .order_by("power_ranking", "-team__overall_rating")
            .annotate(
                pt_diff=F("points_for") - F("points_against"),
                win_pct=Case(
                    When(
                        wins__gt=0,
                        then=Cast("wins", FloatField())
                        / (F("wins") + F("losses") + F("ties")),
                    ),
                    default=F("wins"),
                    output_field=FloatField(),
                ),
            )
        )

        return standings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        League = apps.get_model("leagues.League")
        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)
        entity = self.kwargs.get("entity")

        if entity and entity not in ("conference", "power"):
            raise Http404("Invalid standings entity supplied")
        context["entity"] = entity

        context["division_standings"] = (
            TeamStanding.objects.filter(season=season)
            .order_by("division_ranking", "-team__overall_rating")
            .annotate(
                pt_diff=F("points_for") - F("points_against"),
                win_pct=Case(
                    When(
                        wins__gt=0,
                        then=Cast("wins", FloatField())
                        / (F("wins") + F("losses") + F("ties")),
                    ),
                    default=F("wins"),
                    output_field=FloatField(),
                ),
            )
        )

        context["conference_standings"] = (
            TeamStanding.objects.filter(season=season)
            .order_by("conference_ranking", "-team__overall_rating")
            .annotate(
                pt_diff=F("points_for") - F("points_against"),
                win_pct=Case(
                    When(
                        wins__gt=0,
                        then=Cast("wins", FloatField())
                        / (F("wins") + F("losses") + F("ties")),
                    ),
                    default=F("wins"),
                    output_field=FloatField(),
                ),
            )
        )

        return context


class AdvanceSeasonFormView(LeagueOwnerMixin, LeagueContextMixin, FormView):
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
