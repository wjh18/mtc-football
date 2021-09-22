from .models import (League, Player, Team, UserTeam,
                     Season, Matchup, TeamStanding,
                     Conference, Division
)
from leagues.utils.progress_season import progress_season
from leagues.utils.update_standings import (
    update_standings_for_byes,
    update_standings
)

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.http import HttpResponse
from django.contrib import messages


# Custom Mixins


# Permissions Mixins


class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user == self.get_object().user

    def handle_no_permission(self):
        return HttpResponse(
            'Sorry, only league owners have access to this page.'
        )


class LeagueOwnerCanViewTeamsMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        league = League.objects.get(id=self.kwargs['league'])
        return self.request.user == league.user

    def handle_no_permission(self):
        return HttpResponse(
            'Sorry, only league owners have access to this page.'
        )


# League Views


class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    context_object_name = 'league_list'
    template_name = 'leagues/league/league_list.html'
    login_url = 'account_login'

    def get_queryset(self):
        return League.objects.filter(user=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, DetailView):
    model = League
    context_object_name = 'league'
    template_name = 'leagues/league/league_detail.html'
    login_url = 'account_login'


class LeagueCreateView(LoginRequiredMixin, CreateView):
    model = League
    fields = ['name', 'gm_name']
    template_name = 'leagues/league/league_create.html'
    success_message = 'League successfully created.'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('team_list', args=[self.object.pk])


class LeagueUpdateView(LeagueOwnerMixin, UpdateView):
    model = League
    fields = ['name', 'gm_name']
    template_name = 'leagues/league/league_update.html'
    success_message = 'League successfully updated.'


class LeagueDeleteView(LeagueOwnerMixin, DeleteView):
    model = League
    success_url = reverse_lazy('league_list')
    template_name = 'leagues/league/league_delete.html'
    success_message = 'League successfully deleted.'


# Team Views


class TeamListView(LeagueOwnerCanViewTeamsMixin, ListView):
    model = Team
    context_object_name = 'team_list'
    template_name = 'leagues/team/team_list.html'
    login_url = 'account_login'

    def get_queryset(self):
        return Team.objects.filter(league=self.kwargs['league'])

    def get_context_data(self, **kwargs):
        # Add context data from URL kwargs for the teams' league
        context = super(TeamListView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        league = League.objects.get(id=league_uuid)
        context['league'] = league
        if UserTeam.objects.filter(league=league).exists():
            context['user_team'] = True
        else:
            context['user_team'] = False

        return context


class TeamDetailView(LeagueOwnerCanViewTeamsMixin, DetailView):
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/team_detail.html'
    login_url = 'account_login'

    def get_context_data(self, **kwargs):
        # Add context data from URL kwargs for the teams' league
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        league = League.objects.get(id=league_uuid)
        context['league'] = league
        if UserTeam.objects.filter(league=league, team=self.object).exists():
            context['user_team'] = UserTeam.objects.get(
                league=league, team=self.object)
        else:
            context['user_team'] = False
        return context


class TeamRosterView(LeagueOwnerCanViewTeamsMixin, ListView):
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/team_roster.html'
    login_url = 'account_login'

    def get_context_data(self, **kwargs):
        # Add context data from URL kwargs for the teams' league
        context = super(TeamRosterView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        team_uuid = self.kwargs['pk']
        context['league'] = League.objects.get(id=league_uuid)
        context['team'] = Team.objects.get(id=team_uuid)
        context['contracts'] = Team.objects.get(id=team_uuid).contracts.all()
        return context


class DepthChartView(LeagueOwnerCanViewTeamsMixin, ListView):
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/depth_chart.html'
    login_url = 'account_login'

    def get_context_data(self, **kwargs):
        context = super(DepthChartView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        team_uuid = self.kwargs['pk']
        context['league'] = League.objects.get(id=league_uuid)
        context['team'] = Team.objects.get(id=team_uuid)
        contracts = Team.objects.get(id=team_uuid).contracts.all()
        position = self.kwargs.get('position', 'QB')
        players = Player.objects.filter(
            id__in=contracts.values('player_id'))
        context['positions'] = list(dict.fromkeys(
            [player.position for player in players]))
        context['players'] = Player.objects.filter(
            id__in=contracts.values('player_id'), position=position).order_by('-overall_rating')
        return context

def update_user_team(request, league):

    if request.method == 'POST':
        league = get_object_or_404(League, pk=league)
        try:
            selected_team = league.teams.get(pk=request.POST['teams'])
        except (KeyError, Team.DoesNotExist):
            # Redisplay the team selection page with an error.
            return render(request, 'leagues/team/team_list.html', {
                'league': league,
                'error_message': "You didn't select a team.",
            })
        else:
            UserTeam.objects.create(league=league, team=selected_team)
            # messages.add_message(
            #     request, messages.SUCCESS, f'You are now the GM of the {selected_team.location} {selected_team.name}')
            return HttpResponseRedirect(reverse('team_detail', args=[league.id, selected_team.id]))

# Player views


class PlayerDetailView(LeagueOwnerCanViewTeamsMixin, DetailView):
    model = Player
    context_object_name = 'player'
    template_name = 'leagues/player/player_detail.html'
    login_url = 'account_login'

    def get_context_data(self, **kwargs):
        context = super(PlayerDetailView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        team_uuid = self.kwargs['team']
        context['league'] = League.objects.get(id=league_uuid)
        context['team'] = Team.objects.get(id=team_uuid)
        return context


# League views

def advance_days(request, league, days):
    if request.method == 'GET':
        league = get_object_or_404(League, pk=league)
        season = get_object_or_404(Season, league=league, is_current=True)
        current_week = season.week_number
        matchups = Matchup.objects.filter(
            season=season, week_number=current_week)

        # For teams on a bye week, update their standings
        update_standings_for_byes(season, current_week)

        # Get scores and results for the current week's matchups, then update standings
        update_standings(season, current_week, matchups)

        # Progress season by X days and save instance
        progress_season(season, days)

        # Success message
        messages.add_message(request, messages.SUCCESS, 'Advanced one week.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class TeamStandingsView(LeagueOwnerCanViewTeamsMixin, ListView):
    model = TeamStanding
    context_object_name = 'standings'
    template_name = 'leagues/team/team_standings.html'
    login_url = 'account_login'

    def get_queryset(self):
        league = self.kwargs['league']
        season = get_object_or_404(Season, league=league, is_current=True)
        standings = TeamStanding.objects.filter(
            season=season, week_number=season.week_number).order_by('-wins', 'losses', '-points_for', 'points_against')

        return standings

    def get_context_data(self, **kwargs):
        # Add context data from URL kwargs for the teams' league
        context = super(TeamStandingsView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        league = League.objects.get(id=league_uuid)
        context['afc'] = Conference.objects.get(name='AFC', league=league)
        context['nfc'] = Conference.objects.get(name='NFC', league=league)
        context['league'] = league
        context['season'] = get_object_or_404(
            Season, league=league, is_current=True)
        context['type'] = self.kwargs.get('type')
        if UserTeam.objects.filter(league=league).exists():
            context['user_team'] = True
        else:
            context['user_team'] = False

        return context
