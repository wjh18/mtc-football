from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.urls import reverse
from .models import League, Team

from django.http import HttpResponse


# Custom Mixins

## Permissions Mixins

class LeagueOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user == self.get_object().commissioner

    def handle_no_permission(self):
        return HttpResponse(
            'Sorry, only league owners have access to this page.'
        )


class LeagueOwnerCanViewTeamsMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        league = League.objects.get(id=self.kwargs['league'])
        return self.request.user == league.commissioner


# League Views

class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    context_object_name = 'league_list'
    template_name = 'leagues/league/league_list.html'
    login_url = 'account_login'

    def get_queryset(self):
        return League.objects.filter(commissioner=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, DetailView):
    model = League
    context_object_name = 'league'
    template_name = 'leagues/league/league_detail.html'
    login_url = 'account_login'


class LeagueCreateView(LoginRequiredMixin, CreateView):
    model = League
    fields = ['name', 'commissioner_name']
    template_name = 'leagues/league/league_create.html'

    def form_valid(self, form):
        form.instance.commissioner = self.request.user
        return super().form_valid(form)


class LeagueUpdateView(LeagueOwnerMixin, UpdateView):
    model = League
    fields = ['name', 'commissioner_name']
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
        # Get context data from URL kwargs for the teams' league
        context = super(TeamListView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        context['league'] = League.objects.get(id=league_uuid)
        return context


class TeamDetailView(LeagueOwnerCanViewTeamsMixin, DetailView):
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/team_detail.html'
    login_url = 'account_login'

    
class TeamRosterView(LeagueOwnerCanViewTeamsMixin, ListView):
    model = Team
    context_object_name = 'team'
    template_name = 'leagues/team/team_roster.html'
    login_url = 'account_login'

    def get_context_data(self, **kwargs):
        # Get context data from URL kwargs for the teams' league
        context = super(TeamRosterView, self).get_context_data(**kwargs)
        league_uuid = self.kwargs.get('league')
        team_uuid = self.kwargs['pk']
        context['league'] = League.objects.get(id=league_uuid)
        context['team'] = Team.objects.get(id=team_uuid)
        return context
        # team_uuid = Team.objects.get(id=self.kwargs['pk'])