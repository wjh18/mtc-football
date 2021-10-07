from django.urls import path
from .views import HomePageView, AboutPageView, ContactPageView

app_name = 'pages'

urlpatterns = [
    path('contact/', ContactPageView.as_view(), name='contact'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('', HomePageView.as_view(), name='home'),
]