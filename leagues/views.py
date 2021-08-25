from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from .models import League, Player, Team, UserTeam

from django.http import HttpResponse


# Custom Mixins

## Permissions Mixins

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('team_list', args=[self.object.pk])


class LeagueUpdateView(LeagueOwnerMixin, UpdateView):
    model = League
    fields = ['name', 'gm_name']
    template_name = 'leagues/league/league_update.html'


class LeagueDeleteView(LeagueOwnerMixin, DeleteView):
    model = League
    success_url = reverse_lazy('league_list')
    template_name = 'leagues/league/league_delete.html'


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
            context['user_team'] = UserTeam.objects.get(league=league, team=self.object)
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
            return HttpResponseRedirect(reverse('team_detail', args=[league.id, selected_team.id]))


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
