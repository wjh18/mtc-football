# Django imports
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Case, F, FloatField, Q, When
from django.db.models.fields import BooleanField
from django.db.models.functions import Cast
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.leagues.forms import AdvanceSeasonForm, TeamSelectForm
from apps.leagues.utils.season import advance_season_by_weeks

# App imports
from .models import League, Matchup, Player, Season, Team, TeamStanding, UserTeam

# Custom Mixins & Decorators


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
        context["season"] = Season.objects.get(league=league, is_current=True)

        if self.kwargs.get("team"):
            team_slug = self.kwargs["team"]
            context["team"] = Team.objects.get(league=league, slug=team_slug)

        return context


# Permissions Mixins & Decorators


class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for verifying user league ownership in class-based views.
    """

    def test_func(self):
        if self.kwargs.get("league"):
            league = League.objects.get(slug=self.kwargs["league"])
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


# League Views


class LeagueListView(LoginRequiredMixin, ListView):
    """
    List the logged-in user's active leagues.
    """

    model = League
    context_object_name = "leagues"
    template_name = "leagues/league/league_list.html"

    def get_queryset(self):
        return League.objects.filter(user=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View an individual league's details.
    """

    model = League
    context_object_name = "league"
    template_name = "leagues/league/league_detail.html"


class LeagueCreateView(LoginRequiredMixin, CreateView):
    """
    Create a league and redirect to its list of teams.
    """

    model = League
    fields = ["name", "gm_name"]
    template_name = "leagues/league/league_create.html"
    success_message = "Your league has been created successfully."

    def form_valid(self, form):
        """Overriden to add success message"""
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("leagues:team_list", args=[self.object.slug])


class LeagueUpdateView(LeagueOwnerMixin, LeagueContextMixin, UpdateView):
    """
    Update an individual league's details.
    """

    model = League
    fields = ["name", "gm_name"]
    template_name = "leagues/league/league_update.html"
    success_message = "Your league has been updated successfully."

    def form_valid(self, form):
        """Overriden to add success message"""
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class LeagueDeleteView(LeagueOwnerMixin, LeagueContextMixin, DeleteView):
    """
    Delete an individual league.
    """

    model = League
    success_url = reverse_lazy("leagues:league_list")
    template_name = "leagues/league/league_delete.html"
    success_message = "Your league has been deleted sucessfully."

    def form_valid(self, form):
        """Overriden to add success message"""
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class WeeklyMatchupsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View weekly matchups for the active league and its current season.
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "leagues/league/matchups.html"

    def get_queryset(self):
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
                        home_team__division__conference__name="American",
                        away_team__division__conference__name="American",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                is_national=Case(
                    When(
                        home_team__division__conference__name="National",
                        away_team__division__conference__name="National",
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
    template_name = "leagues/league/matchup_detail.html"

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs["league"])
        return (
            Matchup.objects.filter(season__league=league)
            .annotate(
                is_american=Case(
                    When(
                        home_team__division__conference__name="American",
                        away_team__division__conference__name="American",
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                is_national=Case(
                    When(
                        home_team__division__conference__name="National",
                        away_team__division__conference__name="National",
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


class LeagueStandingsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View team standings by division, conference, or league-wide.
    """

    model = TeamStanding
    context_object_name = "standings"
    template_name = "leagues/league/standings.html"

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        standings = (
            TeamStanding.objects.filter(season=season, week_number=week_number)
            .order_by("ranking__power_ranking", "-team__overall_rating")
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

        league = League.objects.get(slug=self.kwargs["league"])
        season = Season.objects.get(league=league, is_current=True)
        entity = self.kwargs.get("entity")

        if entity and entity not in ("conference", "power"):
            raise Http404("Invalid standings entity supplied")
        context["entity"] = entity

        # Show final regular season standings during playoffs
        if season.week_number >= 19:
            week_number = 19
        else:
            week_number = season.week_number

        context["division_standings"] = (
            TeamStanding.objects.filter(season=season, week_number=week_number)
            .order_by("ranking__division_ranking", "-team__overall_rating")
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
            TeamStanding.objects.filter(season=season, week_number=week_number)
            .order_by("ranking__conference_ranking", "-team__overall_rating")
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


class PlayoffsView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View playoff matchups / bracket for the current season
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "leagues/league/playoffs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        matchups = Matchup.objects.filter(season=context["season"], is_postseason=True)

        american_case = Case(
            When(
                home_team__division__conference__name="American",
                away_team__division__conference__name="American",
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        )
        national_case = Case(
            When(
                home_team__division__conference__name="National",
                away_team__division__conference__name="National",
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


class AdvanceSeasonFormView(LeagueOwnerMixin, LeagueContextMixin, FormView):
    """
    Advance the regular season, playoffs or to the next season
    based on the number of weeks submitted in the form.
    """

    form_class = AdvanceSeasonForm
    template_name = "leagues/forms/advance_season_form.html"

    def post(self, request, *args, **kwargs):
        """
        Override FormView post() method to ensure the user has
        selected a team before advancing the season.
        """
        context = self.get_context_data()
        league = context["league"]

        try:
            league.userteam
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


# Team Views


class TeamSelectFormView(LeagueOwnerMixin, LeagueContextMixin, FormView):
    """
    Create the league's user-controlled team based on the
    league owner's team selection submitted in the form.
    """

    form_class = TeamSelectForm
    template_name = "leagues/forms/team_select_form.html"

    def form_valid(self, form):
        # Get League context provided by LeagueContextMixin
        context = self.get_context_data()
        league = context["league"]

        # Create UserTeam based on selected Team in form data.
        team = form.cleaned_data["team"]
        selected_team = league.teams.get(pk=team.pk)
        UserTeam.objects.create(league=league, team=selected_team)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"You are now the GM of the \
            {selected_team.location} {selected_team.name}.",
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add league to form kwargs to filter teams
        kwargs["league"] = self.kwargs["league"]
        return kwargs

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", "/")


class TeamListView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    List the teams belonging to the active league and provide context
    indicating whether the user's team has been selected.
    """

    model = Team
    context_object_name = "team_list"
    template_name = "leagues/league/team_list.html"

    def get_queryset(self):
        return Team.objects.filter(league__slug=self.kwargs["league"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add TeamSelectForm as context to team_list.html
        context["form"] = TeamSelectForm(form_kwargs={"league": context["league"]})

        return context


class TeamDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual team.
    """

    model = Team
    context_object_name = "team"
    template_name = "leagues/team/team_detail.html"

    def get_queryset(self):
        league_slug = self.kwargs["league"]
        return Team.objects.filter(league__slug=league_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Context for team select dropdown
        league_slug = self.kwargs["league"]
        context["team_list"] = Team.objects.filter(league__slug=league_slug)

        return context


class TeamRosterView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View an individual team's roster and player attributes,
    sorted by overall rating.
    """

    model = Team
    context_object_name = "team"
    template_name = "leagues/team/roster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = context["team"]
        context["contracts"] = team.contracts.all()

        # Context for team select dropdown
        league_slug = self.kwargs["league"]
        context["team_list"] = Team.objects.filter(league__slug=league_slug)

        return context


class DepthChartView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View an individual team's depth chart by position.
    """

    model = Team
    context_object_name = "team"
    template_name = "leagues/team/depth_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = context["team"]
        contracts = team.contracts.all()
        player_ids = contracts.values("player_id")
        players = Player.objects.filter(id__in=player_ids)

        positions = list(dict.fromkeys([player.position for player in players]))
        position = self.kwargs.get("position", "QB")

        if position not in positions:
            raise Http404("Position does not exist")

        context["positions"] = positions
        context["active_position"] = position
        context["players"] = Player.objects.filter(
            id__in=player_ids, position=position
        ).order_by("-overall_rating")

        # Context for team select dropdown
        league_slug = self.kwargs["league"]
        context["team_list"] = Team.objects.filter(league__slug=league_slug)

        return context


class TeamScheduleView(LeagueOwnerMixin, LeagueContextMixin, ListView):
    """
    View the schedule of matchups for an individual team's current season.
    """

    model = Matchup
    context_object_name = "matchups"
    template_name = "leagues/team/schedule.html"

    def get_queryset(self):
        league = League.objects.get(slug=self.kwargs["league"])
        team = Team.objects.get(league=league, slug=self.kwargs["team"])
        season = Season.objects.get(league=league, is_current=True)
        matchups = Matchup.objects.filter(
            Q(home_team=team) | Q(away_team=team), season=season
        ).order_by("week_number")

        return matchups

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = context["team"]
        season = context["season"]
        context["bye_week"] = team.check_bye_week(season)

        # Context for team select dropdown
        league_slug = self.kwargs["league"]
        context["team_list"] = Team.objects.filter(league__slug=league_slug)

        return context


# Player views


class PlayerDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View additional details about an individual player in a league.
    """

    model = Player
    context_object_name = "player"
    template_name = "leagues/player/player_detail.html"
