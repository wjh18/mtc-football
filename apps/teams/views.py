from django.apps import apps
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.views.generic import DetailView, FormView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import LeagueOwnerMixin

from .forms import TeamSelectForm
from .models import Team, UserTeam


class TeamSelectFormView(LeagueOwnerMixin, LeagueContextMixin, FormView):
    """
    Create the league's user-controlled team based on the
    league owner's team selection submitted in the form.
    """

    form_class = TeamSelectForm
    template_name = "teams/forms/team_select_form.html"

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
    template_name = "teams/team_list.html"

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
    template_name = "teams/team_detail.html"

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
    template_name = "teams/roster.html"

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
    template_name = "teams/depth_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Player = apps.get_model("personnel.Player")

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

    model = apps.get_model("matchups.Matchup")
    context_object_name = "matchups"
    template_name = "teams/schedule.html"

    def get_queryset(self):
        League = apps.get_model("leagues.League")
        Matchup = apps.get_model("matchups.Matchup")
        Season = apps.get_model("seasons.Season")

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
