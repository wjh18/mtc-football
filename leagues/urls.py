from django.urls import path
from . import views

urlpatterns = [
    path('', views.LeagueListView.as_view(), name='league_list'),
    path('<uuid:pk>/', views.LeagueDetailView.as_view(), name='league_detail'),
    path('new/', views.LeagueCreateView.as_view(), name='league_create'),
    path('<uuid:pk>/edit/', views.LeagueUpdateView.as_view(), name='league_edit'),
    path('<uuid:pk>/delete/', views.LeagueDeleteView.as_view(), name='league_delete'),
    path('<uuid:league>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<uuid:league>/teams/update-user-team/', views.update_user_team, name='update_user_team' ),
    path('<uuid:league>/teams/<uuid:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('<uuid:league>/teams/<uuid:pk>/roster/', views.TeamRosterView.as_view(), name='team_roster'),
]
