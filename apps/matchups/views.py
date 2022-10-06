from django.apps import apps
from django.db.models import Case, When
from django.db.models.fields import BooleanField
from django.http import Http404
from django.views.generic import DetailView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import LeagueOwnerMixin

from .models import Matchup


class WeeklyMatchupsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/matchups.html"

    def get_queryset(self):
        League = apps.get_model("leagues.League")
        Season = apps.get_model("seasons.Season")

        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)

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

        matchups = (
            Matchup.objects.filter(season=season, week_number=week_number)
            .annotate(
                is_american=Case(
                    When(
                        home_team__conference__name="American",
                        away_team__conference__name="American",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                is_national=Case(
                    When(
                        home_team__conference__name="National",
                        away_team__conference__name="National",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )

        return matchups

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        League = apps.get_model("leagues.League")
        Season = apps.get_model("seasons.Season")

        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)

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

        context["week_num"] = week_number
        context["num_weeks"] = weeks

        if week_number <= 18:
            context["bye_teams"] = season.get_byes(week_number)

        return context


class MatchupDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details related to an individual matchup.
    """

    model = Matchup
    context_object_name = "matchup"
    template_name = "matchups/matchup_detail.html"

    def get_queryset(self):
        League = apps.get_model("leagues.League")

        league = League.objects.get(slug=self.kwargs["league"])
        return (
            Matchup.objects.filter(season__league=league)
            .annotate(
                is_american=Case(
                    When(
                        home_team__conference__name="American",
                        away_team__conference__name="American",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                is_national=Case(
                    When(
                        home_team__conference__name="National",
                        away_team__conference__name="National",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )


class PlayoffsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "matchups/playoffs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        matchups = Matchup.objects.filter(season=context["season"], is_postseason=True)

        american_case = Case(
            When(
                home_team__conference__name="American",
                away_team__conference__name="American",
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )
        national_case = Case(
            When(
                home_team__conference__name="National",
                away_team__conference__name="National",
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )

        context["wildcard_matchups"] = (
            matchups.filter(week_number=19)
            .annotate(is_american=american_case, is_national=national_case)
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )
        context["divisional_matchups"] = (
            matchups.filter(week_number=20)
            .annotate(is_american=american_case, is_national=national_case)
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )
        context["conference_matchups"] = (
            matchups.filter(week_number=21)
            .annotate(is_american=american_case, is_national=national_case)
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )
        context["championship_matchups"] = (
            matchups.filter(week_number=22)
            .annotate(is_american=american_case, is_national=national_case)
            .order_by(
                "-is_american", "-is_national", "-is_divisional", "-is_conference"
            )
        )

        return context
