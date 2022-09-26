from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin (default)
    path('admin/', admin.site.urls),

    # User management (Django allauth)
    path('accounts/', include('allauth.urls')),

    # Local apps
    path('', include('apps.pages.urls', namespace='pages')),
    path('leagues/', include('apps.leagues.urls', namespace='leagues')),
    path('simulation/', include('apps.simulation.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]
