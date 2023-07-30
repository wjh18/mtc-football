from django.urls import path

from . import views

app_name = 'matchups'

urlpatterns = [
    path('<slug:league>/matchups/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups'),
    path('<slug:league>/matchups/week/<int:week_num>/',
         views.WeeklyMatchupsView.as_view(), name='weekly_matchups_by_week'),
    path('<slug:league>/matchups/<slug:slug>/',
         views.MatchupDetailView.as_view(), name='matchup_detail'),
    path('<slug:league>/schedule/<slug:team>/',
         views.TeamScheduleView.as_view(), name='team_schedule'),
    path('<slug:league>/playoffs/',
         views.PlayoffsView.as_view(), name='playoffs'),
]
