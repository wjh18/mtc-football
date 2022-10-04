from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .mixins import LeagueContextMixin
from .models import League
from .permissions import LeagueOwnerMixin


class LeagueListView(LoginRequiredMixin, ListView):
    """
    List the logged-in user's active leagues.
    """

    model = League
    context_object_name = "leagues"
    template_name = "leagues/league_list.html"

    def get_queryset(self):
        return League.objects.filter(user=self.request.user)


class LeagueDetailView(LeagueOwnerMixin, LeagueContextMixin, DetailView):
    """
    View an individual league's details.
    """

    model = League
    context_object_name = "league"
    template_name = "leagues/league_detail.html"


class LeagueCreateView(LoginRequiredMixin, CreateView):
    """
    Create a league and redirect to its list of teams.
    """

    model = League
    fields = ["name", "gm_name"]
    template_name = "leagues/league_create.html"
    success_message = "Your league has been created successfully."

    def form_valid(self, form):
        """Overriden to add success message"""
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("teams:team_list", args=[self.object.slug])


class LeagueUpdateView(LeagueOwnerMixin, LeagueContextMixin, UpdateView):
    """
    Update an individual league's details.
    """

    model = League
    fields = ["name", "gm_name"]
    template_name = "leagues/league_update.html"
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
    template_name = "leagues/league_delete.html"
    success_message = "Your league has been deleted sucessfully."

    def form_valid(self, form):
        """Overriden to add success message"""
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
