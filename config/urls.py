from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic.base import TemplateView

from apps.pages.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    # General
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt',TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # User management
    path('accounts/', include('allauth.urls')),
    # Local apps
    path('', include('apps.pages.urls', namespace='pages')),
    path('leagues/', include('apps.leagues.urls', namespace='leagues')),
    path('simulation/', include('apps.simulation.urls')),
    # 3rd-party apps
    path('__debug__/', include('debug_toolbar.urls')),
]
