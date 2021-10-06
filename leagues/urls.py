from django.urls import path
from . import views

app_name = 'leagues'
urlpatterns = [
    # Generic League views
    path('', views.LeagueListView.as_view(), name='league_list'),
    path('new/', views.LeagueCreateView.as_view(), name='league_create'),
    path('<slug:slug>/',
         views.LeagueDetailView.as_view(), name='league_detail'),
    path('<slug:slug>/edit/',
         views.LeagueUpdateView.as_view(), name='league_edit'),
    path('<slug:slug>/delete/',
         views.LeagueDeleteView.as_view(), name='league_delete'),
    # Generic Team views
    path('<slug:league>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:league>/teams/update-user-team/',
         views.update_user_team, name='update_user_team'),
    path('<slug:league>/teams/<slug:slug>/',
         views.TeamDetailView.as_view(), name='team_detail'),
    # Team roster and depth chart views
    path('<slug:league>/teams/<slug:team>/roster/',
         views.TeamRosterView.as_view(), name='team_roster'),
    path('<slug:league>/teams/<slug:team>/depth-chart/',
         views.DepthChartView.as_view(), name='depth_chart'),
    path('<slug:league>/teams/<slug:team>/depth-chart/<str:position>/',
         views.DepthChartView.as_view(), name='depth_chart_pos'),
    # Generic Player views
    path('<slug:league>/teams/<slug:team>/roster/<slug:slug>/',
         views.PlayerDetailView.as_view(), name='player_detail'),
    # League advancement views
    path('<slug:league>/advance-regular-season/<int:weeks>/',
         views.advance_regular_season, name='advance_regular_season'),
    path('<slug:league>/advance-regular-season/',
         views.advance_regular_season, name='advance_regular_season_full'),
    path('<slug:league>/advance-playoffs/',
         views.advance_playoffs, name='advance_playoffs'),
    # League standings views
    path('<slug:league>/standings/',
         views.LeagueStandingsView.as_view(), name='league_standings'),
    path('<slug:league>/standings/<str:type>/',
         views.LeagueStandingsView.as_view(), name='league_standings_type'),
    # League schedule and matchup views
    path('<slug:league>/teams/<slug:team>/schedule/',
         views.TeamScheduleView.as_view(), name='team_schedule'),
    path('<slug:league>/weekly-matchups/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups'),
    path('<slug:league>/weekly-matchups/<int:week_num>/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups_by_week'),
    path('<slug:league>/weekly-matchups/<slug:slug>/',
         views.MatchupDetailView.as_view(), name='matchup_detail'),
    path('<slug:league>/playoffs/',
         views.PlayoffsView.as_view(), name='playoffs'),
]
