from django.urls import path
from . import views

urlpatterns = [
    path('', views.LeagueListView.as_view(), name='league_list'),
    path('<int:pk>/', views.LeagueDetailView.as_view(), name='league_detail'),
    path('new/', views.LeagueCreateView.as_view(), name='league_create'),
    path('<int:pk>/edit/', views.LeagueUpdateView.as_view(), name='league_edit'),
    path('<int:pk>/delete/', views.LeagueDeleteView.as_view(), name='league_delete'),
    path('<int:league>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<int:league>/teams/update-user-team/',
         views.update_user_team, name='update_user_team'),
    path('<int:league>/teams/<int:pk>/',
         views.TeamDetailView.as_view(), name='team_detail'),
    path('<int:league>/teams/<int:team>/roster/',
         views.TeamRosterView.as_view(), name='team_roster'),
    path('<int:league>/teams/<int:team>/depth-chart/',
         views.DepthChartView.as_view(), name='depth_chart'),
    path('<int:league>/teams/<int:team>/depth-chart/<str:position>/',
         views.DepthChartView.as_view(), name='depth_chart_pos'),
    path('<int:league>/teams/<int:team>/roster/<int:pk>/',
         views.PlayerDetailView.as_view(), name='player_detail'),
    path('<int:league>/advance-regular-season/<int:weeks>/',
         views.advance_regular_season, name='advance_regular_season'),
    path('<int:league>/advance-regular-season/',
         views.advance_regular_season, name='advance_regular_season_full'),
    path('<int:league>/standings/',
         views.LeagueStandingsView.as_view(), name='league_standings'),
    path('<int:league>/standings/<str:type>/',
         views.LeagueStandingsView.as_view(), name='league_standings_type'),
    path('<int:league>/teams/<int:team>/schedule/',
         views.TeamScheduleView.as_view(), name='team_schedule'),
    path('<int:league>/weekly-matchups/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups'),
    path('<int:league>/weekly-matchups/<int:week_num>/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups_by_week'),
    path('<int:league>/weekly-matchups/matchup/<int:pk>/',
         views.MatchupDetailView.as_view(), name='matchup_detail'),
]
