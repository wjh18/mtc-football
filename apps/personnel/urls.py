from django.urls import path

from . import views

app_name = 'personnel'

urlpatterns = [
    path('<slug:league>/players/<slug:slug>/',
         views.PlayerDetailView.as_view(), name='player_detail'),
]
