from django.urls import path

from . import views

app_name = 'teams'

urlpatterns = [
    path('<slug:league>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:league>/teams/team-select/',
         views.TeamSelectFormView.as_view(), name='team_select'),
    path('<slug:league>/teams/<slug:slug>/',
         views.TeamDetailView.as_view(), name='team_detail'),
    path('<slug:league>/teams/<slug:team>/roster/',
         views.TeamRosterView.as_view(), name='team_roster'),
    path('<slug:league>/teams/<slug:team>/depth-chart/',
         views.DepthChartView.as_view(), name='depth_chart'),
    path('<slug:league>/teams/<slug:team>/depth-chart/<str:position>/',
         views.DepthChartView.as_view(), name='depth_chart_pos'),
    path('<slug:league>/teams/<slug:team>/schedule/',
         views.TeamScheduleView.as_view(), name='team_schedule'),
]
