from django.apps import apps
from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404
from django.views.generic import DetailView, FormView, ListView

from apps.leagues.mixins import LeagueContextMixin
from apps.leagues.permissions import IsLeagueOwner

from .forms import TeamSelectForm
from .mixins import LeagueTeamsMixin
from .models import Team, UserTeam


class TeamSelectFormView(IsLeagueOwner, LeagueContextMixin, FormView):
    """
    Create the league's user-controlled team based on the
    league owner's team selection submitted in the form.
    """

    form_class = TeamSelectForm
    template_name = "teams/forms/team_select_form.html"

    def form_valid(self, form):
        context = self.get_context_data()
        league = context["league"]  # From LeagueContextMixin

        team = form.cleaned_data["team"]
        user_team_exists = True

        try:
            user_team = UserTeam.objects.get(league=league, is_active_team=True)
            messages.add_message(
                self.request,
                messages.WARNING,
                f"You're already the GM of the {user_team.team}.",
            )
        except UserTeam.DoesNotExist:
            user_team_exists = False

        if not user_team_exists:
            try:
                UserTeam.objects.create(league=league, team=team)
            except IntegrityError:
                raise Http404("There was an error selecting your team.")
            messages.add_message(
                self.request,
                messages.SUCCESS,
                f"You are now the GM of the {team}.",
            )

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add league to form kwargs to filter teams
        kwargs["league"] = self.kwargs["league"]
        return kwargs

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", "/")


class TeamListView(IsLeagueOwner, LeagueTeamsMixin, LeagueContextMixin, ListView):
    """
    List the teams belonging to the active league and provide context
    indicating whether the user's team has been selected.
    """

    model = Team
    context_object_name = "teams"
    template_name = "teams/team_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add TeamSelectForm as context to team_list.html
        context["form"] = TeamSelectForm(form_kwargs={"league": context["league"]})

        return context


class TeamDetailView(IsLeagueOwner, LeagueContextMixin, DetailView):
    """
    View additional details about an individual team.
    """

    model = Team
    context_object_name = "team"
    template_name = "teams/team_detail.html"


class TeamRosterView(IsLeagueOwner, LeagueTeamsMixin, LeagueContextMixin, DetailView):
    """
    View an individual team's roster and player attributes,
    sorted by overall rating.
    """

    model = Team
    context_object_name = "team"
    template_name = "teams/roster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Player = apps.get_model("personnel.Player")

        contracts = self.object.contracts.all()
        player_ids = contracts.values("player_id")
        context["players"] = Player.objects.filter(id__in=player_ids).order_by(
            "-overall_rating"
        )

        return context


class DepthChartView(IsLeagueOwner, LeagueTeamsMixin, LeagueContextMixin, DetailView):
    """
    View an individual team's depth chart by position.
    """

    model = Team
    context_object_name = "team"
    template_name = "teams/depth_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Player = apps.get_model("personnel.Player")

        contracts = self.object.contracts.all()
        player_ids = contracts.values("player_id")
        players = Player.objects.filter(id__in=player_ids)

        positions = list(dict.fromkeys([player.position for player in players]))
        position = self.request.GET.get("position", "QB")

        if position not in positions:
            raise Http404("Position does not exist")

        context["positions"] = positions
        context["active_position"] = position
        context["players"] = players.filter(position=position).order_by(
            "-overall_rating"
        )

        return context
