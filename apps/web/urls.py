from django.urls import path
from django.views.generic import TemplateView

from .views import AboutPageView, ContactPageView, HomePageView

app_name = 'web'

urlpatterns = [
    path('contact/', ContactPageView.as_view(), name='contact'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('', HomePageView.as_view(), name='home'),
    path('404/', TemplateView.as_view(template_name='base/404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='base/500.html'), name='500'),
    path('403/', TemplateView.as_view(template_name='base/403.html'), name='403'),
    path('400/', TemplateView.as_view(template_name='base/400.html'), name='400'),
]
