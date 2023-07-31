from django.urls import path

from . import views

app_name = 'seasons'

urlpatterns = [
    path('<slug:league>/advance-season/',
         views.AdvanceSeasonFormView.as_view(), name='advance_season'),
    path('<slug:league>/standings/',
         views.LeagueStandingsView.as_view(), name='league_standings'),
]
