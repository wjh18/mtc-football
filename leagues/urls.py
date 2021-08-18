from django.urls import path
from .views import (
    LeagueListView, LeagueDetailView, LeagueCreateView,
    LeagueUpdateView, LeagueDeleteView, TeamListView,
    TeamRosterView,
)

urlpatterns = [
    path('', LeagueListView.as_view(), name='league_list'),
    path('<uuid:pk>/', LeagueDetailView.as_view(), name='league_detail'),
    path('new/', LeagueCreateView.as_view(), name='league_create'),
    path('<uuid:pk>/edit/', LeagueUpdateView.as_view(), name='league_edit'),
    path('<uuid:pk>/delete/', LeagueDeleteView.as_view(), name='league_delete'),
    path('<uuid:league>/teams/', TeamListView.as_view(), name='team_list'),
    path('<uuid:league>/teams/<uuid:pk>/roster/', TeamRosterView.as_view(), name='team_roster'),
]
