from django.urls import include, path

from . import views

leagues_patterns = ([
    path('', views.LeagueListView.as_view(), name='league_list'),
    path('new/', views.LeagueCreateView.as_view(), name='league_create'),
    path('<slug:slug>/',
         views.LeagueDetailView.as_view(), name='league_detail'),
    path('<slug:slug>/edit/',
         views.LeagueUpdateView.as_view(), name='league_update'),
    path('<slug:slug>/delete/',
         views.LeagueDeleteView.as_view(), name='league_delete'),
], 'leagues')

urlpatterns = [
    path('', include(leagues_patterns)),
    path('', include('apps.teams.urls', namespace='teams')),
    path('', include('apps.personnel.urls', namespace='personnel')),
    path('', include('apps.matchups.urls', namespace='matchups')),
    path('', include('apps.seasons.urls', namespace='seasons')),
]
