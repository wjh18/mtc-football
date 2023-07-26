from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('404/', TemplateView.as_view(template_name='errors/404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='errors/500.html'), name='500'),
    path('403/', TemplateView.as_view(template_name='errors/403.html'), name='403'),
    path('400/', TemplateView.as_view(template_name='errors/400.html'), name='400'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.TermsPageView.as_view(), name='terms'),
    path('privacy/', views.PrivacyPageView.as_view(), name='privacy'),
]
