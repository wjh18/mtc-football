from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.urls import reverse
from .models import League


class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    context_object_name = 'league_list'
    template_name = 'leagues/league_list.html'
    login_url = 'account_login'

    def get_queryset(self):
        return League.objects.filter(commissioner=self.request.user)


class LeagueDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = League
    context_object_name = 'league'
    template_name = 'leagues/league_detail.html'
    login_url = 'account_login'

    def test_func(self):
        return self.request.user == self.get_object().commissioner


class LeagueCreateView(LoginRequiredMixin, CreateView):
    model = League
    fields = ['name', 'commissioner_name']
    template_name = 'leagues/league_create.html'

    def form_valid(self, form):
        form.instance.commissioner = self.request.user
        return super().form_valid(form)


class LeagueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = League
    fields = ['name', 'commissioner_name']
    template_name = 'leagues/league_update.html'

    def test_func(self):
        return self.request.user == self.get_object().commissioner


class LeagueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = League
    success_url = reverse_lazy('league_list')
    template_name = 'leagues/league_delete.html'

    def test_func(self):
        return self.request.user == self.get_object().commissioner