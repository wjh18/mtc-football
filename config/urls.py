from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic.base import TemplateView

from apps.web.sitemaps import StaticViewSitemap

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
    path('', include('apps.web.urls', namespace='web')),
    path('leagues/', include('apps.leagues.urls', namespace='leagues')),
    path('simulation/', include('apps.simulation.urls')),
    # 3rd-party apps
    path('__debug__/', include('debug_toolbar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
