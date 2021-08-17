from django.urls import path
from .views import (
    LeagueDetailView, LeagueListView,
    LeagueCreateView, LeagueDeleteView,
    LeagueUpdateView
)

urlpatterns = [
    path('', LeagueListView.as_view(), name='league_list'),
    path('<uuid:pk>/', LeagueDetailView.as_view(), name='league_detail'),
    path('new/', LeagueCreateView.as_view(), name='league_create'),
    path('<uuid:pk>/edit/', LeagueUpdateView.as_view(), name='league_edit'),
    path('<uuid:pk>/delete/', LeagueDeleteView.as_view(), name='league_delete'),
]
